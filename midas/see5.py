# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import collections
import string
import subprocess
import threading


C5_ARGS = [('-X', '10'),
           ('-X', '10', '-b'),
           ('-X', '10', '-r'),
           ('-X', '10', '-r', '-b'),
           ('-w', '-X', '10'),
           ('-w', '-X', '10', '-b'),
           ('-w', '-X', '10', '-r'),
           ('-w', '-X', '10', '-r', '-b')]

def main():
    costs = list(range(40))
    results = dict()
    for arg in C5_ARGS:
        results[arg] = dict()
        for cost, tbl in get_precision_recall_tables('all', costs, arg):
            results[arg][cost] = tbl
    return results

def gather_c5_output(filestem='all', 
                     positive_cls='True', 
                     negative_cls='False'):
    for cost in range(40):
        write_costs_file(filestem, [(negative_cls, positive_cls, cost), ])
        prefix = 'c5_result_costs_{0}'.format(cost)
        threads = []
        for arg in C5_ARGS:
            t = threading.Thread(target=produce_output, 
                                 args=(filestem, arg, prefix))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
            
def produce_output(filestem, args, prefix):
    all_args = list(args) + ['-f', filestem, ]
    output = call_c5(all_args)
    fname = '{0}_{1}_{2}.out'.format(prefix, filestem, '_'.join(args))
    with open(fname, 'w') as fp:
        fp.writelines(output)

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

def get_precision_recall_tables(filestem, costs, c5_args,
                                positive_cls='True', negative_cls='False'):
    for cost in costs:
        write_costs_file(filestem, [(negative_cls, positive_cls, cost), ])
        args = list(c5_args) + ['-f', filestem, ]
        output = call_c5(args)
        yield cost, get_confusion_matrix(output)

def get_confusion_matrix(see5_output, 
                         table_head_identifier='<-classified as'):
    """
    Parses the output of `c5.0' into a nested dictionary. The first
    level of the result is the actual class. The second level its
    classification.
    """
    lines = see5_output.split('\n')
    for i, l in enumerate(lines):
        if table_head_identifier in l:
            tbl_head = i
    try:
        # Counting the number of drawn lines
        cls_cnt = len(lines[tbl_head+1].split())
    except NameError:
        raise ValueError(
            "'{0}' not found in '{1}'".format(table_head_identifier,
                                              see5_output)
            )

    tbl_start = tbl_head + 2
    tbl_foot = tbl_start + cls_cnt
    table = [ l for l in lines[tbl_start:tbl_foot] ]

    result = collections.defaultdict(dict)
    classes = [ row.rsplit(' ', 1)[-1] for row in table ]
    col_ends = [ lines[tbl_head].find('({0})'.format(c)) + 3
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
    
def write_costs_file(filestem, costs):
    with open('{0}.costs'.format(filestem), 'w') as fp:
        fp.writelines('{0}, {1}: {2}'.format(*c) for c in costs)

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
