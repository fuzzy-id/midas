# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import collections
import glob
import os.path
import string
import subprocess
import threading

from midas.compat import irange

C5_ARGS = [('-X', '10'),
           ('-X', '10', '-b'),
           ('-X', '10', '-r'),
           ('-X', '10', '-r', '-b'),
           ('-X', '10', '-w'),
           ('-X', '10', '-w', '-b'),
           ('-X', '10', '-w', '-r'),
           ('-X', '10', '-w', '-r', '-b')]

def run_c5_and_save_output_threaded_per_cost(dst_directory,
                                             filestem='all',
                                             costs_start=0,
                                             costs_end=40,
                                             costs_step=1,
                                             positive_cls='True', 
                                             negative_cls='False'):
    for cost in irange(costs_start, costs_end, costs_step):
        write_costs_file(filestem, [(negative_cls, positive_cls, cost), ])
        threads = []
        for arg in C5_ARGS:
            fname = os.path.join(dst_directory, 
                                 'c5_{0}_result_{1}_{2}'\
                                     .format(filestem, cost, '_'.join(arg)))
            arg_w_fstem = ['-f', filestem, ]
            arg_w_fstem.extend(arg)
            t = threading.Thread(target=run_c5_and_get_output, 
                                 args=(arg_w_fstem, fname))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
            
def write_costs_file(filestem, costs):
    with open('{0}.costs'.format(filestem), 'w') as fp:
        fp.writelines('{0}, {1}: {2}'.format(*c) for c in costs)

def run_c5_and_get_output(args, save_to=None):
    output = call_c5(args)
    if save_to:
        with open(save_to, 'w') as fp:
            fp.writelines(output)
    return output

def call_c5(args, executable='c5.0'):
    cmd = [executable, ]
    cmd.extend(args)
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    assert proc.returncode == 0
    assert err == ''
    return out

def c5_get_confusion_matrix_from_output(c5_args_and_output):
    result = collections.defaultdict(dict)
    for args, output in c5_args_and_output:
        cost = args[0]
        args_key = tuple(args[1:])
        cm = c5_get_confusion_matrix(output)
        result[args_key][cost] = cm
    return result

def iter_c5_args_and_output(path_pattern):
    for fname in glob.glob(path_pattern):
        args = c5_parse_args(fname)
        with open(fname) as fp:
            output = [ l.rstrip() for l in fp.readlines() ]
        yield args, output

def c5_parse_args(fname):
    _, args = fname.split('_result_')
    return args.split('_')

def c5_get_confusion_matrix(see5_output, 
                            table_head_identifier='<-classified as'):
    """
    Parses the output of `c5.0' into a nested dictionary. The first
    level of the result is the actual class. The second level its
    classification.
    """
    for i, l in enumerate(see5_output):
        if table_head_identifier in l:
            tbl_head = i
    try:
        # Counting the number of drawn lines
        cls_cnt = len(see5_output[tbl_head+1].split())
    except NameError:
        raise ValueError(
            "'{0}' not found in '{1}'".format(table_head_identifier,
                                              see5_output)
            )

    tbl_start = tbl_head + 2
    tbl_foot = tbl_start + cls_cnt
    table = [ l for l in see5_output[tbl_start:tbl_foot] ]

    result = collections.defaultdict(dict)
    classes = [ row.rsplit(' ', 1)[-1] for row in table ]
    col_ends = [ see5_output[tbl_head].find('({0})'.format(c)) + 3
                   for c in string.ascii_lowercase[:cls_cnt] ]

    for row_cls, row in zip(classes, table):
        col_start = 0
        for col_end, col_cls in zip(col_ends, classes):
            field = row[col_start:col_end].strip()
            if field == '':
                result[row_cls][col_cls] = 0
            else:
                result[row_cls][col_cls] = int(field)
            col_start = col_end
    return result
    
def calculate_recall_precision(confusion_matrix, 
                               pos_cls='True', 
                               neg_cls='False'):
    tp = confusion_matrix[pos_cls][pos_cls]
    fp = confusion_matrix[neg_cls][pos_cls]
    precision = tp / (tp + fp)
    recall = calculate_tpr(confusion_matrix, pos_cls, neg_cls)
    return (recall, precision)

def calculate_tpr(confusion_matrix, pos_cls='True', neg_cls='False'):
    tp = confusion_matrix[pos_cls][pos_cls]
    fn = confusion_matrix[pos_cls][neg_cls]
    return tp / (tp + fn)

def calculate_fpr(confusion_matrix, pos_cls='True', neg_cls='False'):
    fp = confusion_matrix[neg_cls][pos_cls]
    tn = confusion_matrix[neg_cls][neg_cls]
    return fp / (fp + tn)
