# -*- coding: utf-8 -*-

import datetime
import os
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose import Entry


MIN_DATE = datetime.datetime(1900, 1, 1).strftime(TP_TSTAMP_FORMAT)
ONE_DAY = datetime.timedelta(days=1)

def reducer():
    cache = []
    min_date = os.environ.get('TP_MIN_DATE', MIN_DATE)
    min_date = datetime.datetime.strptime(min_date, TP_TSTAMP_FORMAT)
    for line in sys.stdin:
        entry = line_to_entry(line)
        if entry.date == min_date:
            out(entry)
            min_date += ONE_DAY
            try:
                while cache[0].date == min_date:  # relasing resources
                    out(cache.pop(0))
                    min_date += ONE_DAY
            except IndexError:
                pass
        else:
            for i in range(len(cache) + 1):  # doing an insertion sort
                try:
                    if entry.date < cache[i].date:
                        cache.insert(i, entry)
                        break
                except IndexError:
                    cache.insert(i, entry)
    for entry in cache:
        out(entry)
    return 0

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
    
