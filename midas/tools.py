# -*- coding: utf-8 -*-
""" This module provides common functions which are usually needed in
all other submodules or interactively.
"""

import collections
import datetime
import functools
import itertools
import operator
import os
import os.path
import subprocess

from midas.compat import GzipFile
from midas.compat import ifilter
from midas.compat import imap
from midas.compat import urlparse
import midas.compat as vt_comp

import midas as md


### Functions that work on MapReduce-style 'key\tvalue' lines ###

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def get_key(line, sep='\t'):
    return split_key_value(line, sep)[0]

### Functions that are often needed in interactive use ###

def count_by_key(iterable, keyfunc=lambda o: o):
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
    return (sum(vt_comp.d_itervalues(counter)),
            len(counter), 
            sum(v for v in vt_comp.d_itervalues(counter) if v > 1), 
            sum(1 for v in vt_comp.d_itervalues(counter) if v > 1))

### Functions to query sites and companies ###

SiteCount = collections.namedtuple('SiteCount', ['site', 'count'])

def make_p_empty_attr(attr_name):
    def p_empty_attr(o):
        attr = getattr(o, attr_name)
        return attr is None or attr == ''
    return p_empty_attr

### Useful miscelanious stuff ###

def takewhile_common(list1, list2):
    for a, b in zip(list1, list2):
        if a != b:
            break
        yield a

def iter_ts_until_gap(ts, all_dates):
    first_common = all_dates.index(ts[-1])
    return takewhile_common(ts[::-1], all_dates[first_common::-1])
