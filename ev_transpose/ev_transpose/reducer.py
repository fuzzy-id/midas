# -*- coding: utf-8 -*-

import datetime
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose import Entry


def reducer():
    cache = []
    for line in sys.stdin:
        entry = line_to_entry(line)
        for i in range(len(cache) + 1):  # doing an insertion sort
            try:
                if entry.date < cache[i].date:
                    cache.insert(i, entry)
                    break
            except IndexError:
                cache.insert(i, entry)
    for entry in cache:
        date = datetime.datetime.strftime(entry.date, 
                                          TP_TSTAMP_FORMAT)
        print('{e.name}\t{0}, {e.rank}'.format(date, e=entry))
    return 0

def line_to_entry(line):
    name, tail = line.split('\t')
    date, rank = tail.split(',')
    date = datetime.datetime.strptime(date, TP_TSTAMP_FORMAT)
    rank = int(rank)
    return Entry(name=name, date=date, rank=rank)
