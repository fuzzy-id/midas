# -*- coding: utf-8 -*-
""" This module provides common functions which are usually needed in
all other submodules or interactively.
"""

import collections

from midas.compat import d_itervalues

### Functions that work on MapReduce-style 'key\tvalue' lines ###

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def get_key(line, sep='\t'):
    return split_key_value(line, sep)[0]

### Functions that are often needed in interactive use ###

def identity(o):
    return o

def count_by_key(iterable, keyfunc=identity):
    counter = collections.defaultdict(int)
    for item in iterable:
        counter[keyfunc(item)] += 1
    return counter

def collect_by_key(iterable, keyfunc):
    collected = collections.defaultdict(list)
    for item in iterable:
        collected[keyfunc(item)].append(item)
    return collected

def relation_stats(iterable):
    counter = count_by_key(iterable)
    return (sum(d_itervalues(counter)),
            len(counter), 
            sum(v for v in d_itervalues(counter) if v > 1), 
            sum(1 for v in d_itervalues(counter) if v > 1))

### Functions to query sites and companies ###

def make_p_empty_attr(attr_name):
    def p_empty_attr(o):
        attr = getattr(o, attr_name)
        return attr is None or attr == ''
    return p_empty_attr
