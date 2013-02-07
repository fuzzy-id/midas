# -*- coding: utf-8 -*-

import subprocess

def get_classified_table(see5_output, 
                         first_line_identifier='<-classified as'):
    lines = see5_output.split('\n')
    for i, l in enumerate(lines):
        if first_line_identifier in l:
            break
    else:
        raise ValueError(
            "'{0}' not found in '{1}'".format(first_line_identifier,
                                              see5_output)
            )
    table = [ l.split() for l in lines[i:i+4] ]
    result = dict()
    fst = table[2][-1]
    snd = table[3][-1]
    fst_col_start = lines[i].find('(a)') + 2
    snd_col_start = lines[i].find('(b)') + 2
    result[fst] = dict()
    result[snd] = dict()

    if lines[i+2][fst_col_start] != ' ':
        result[fst][fst] = int(table[2][0])
    else:
        result[fst][fst] = 0

    if lines[i+2][snd_col_start] != ' ':
        result[fst][snd] = int(table[2][1])
    else:
        result[fst][snd] = 0

    if lines[i+3][fst_col_start] != ' ':
        result[snd][fst] = int(table[3][0])
    else:
        result[snd][fst] = 0

    if lines[i+3][snd_col_start] != ' ':
        result[snd][snd] = int(table[3][1])
    else:
        result[snd][snd] = 0

    return result
    
def write_costs_file(filestem, costs):
    with open('{0}.costs'.format(filestem), 'w') as fp:
        fp.writelines('{0}, {1}: {2}'.format(*c) for c in costs)

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
        args = c5_args + ['-f', filestem, ]
        output = call_c5(args)
        yield get_classified_table(output)
