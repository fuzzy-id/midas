# -*- coding: utf-8 -*-

import datetime
import os
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose import Entry


def reducer():
    cache = []
    for line in sys.stdin:
        entry = line_to_entry(line)
        if len(cache) > 0 and cache[0].name != entry.name:
            out_cache(cache)
        cache.append(entry)
    out_cache(cache)
    return 0

def out_cache(cache):
    cache.sort(key=lambda e: e.date)
    while len(cache) > 0:
        out(cache.pop(0))

def line_to_entry(line):
    name, tail = line.split('\t')
    date, rank = tail.split(',')
    date = datetime.datetime.strptime(date, TP_TSTAMP_FORMAT)
    rank = int(rank)
    return Entry(name=name, date=date, rank=rank)

def out(entry):
    date = datetime.datetime.strftime(entry.date, 
                                      TP_TSTAMP_FORMAT)
    print('{e.name}\t{0}, {e.rank}'.format(date, e=entry))
    
