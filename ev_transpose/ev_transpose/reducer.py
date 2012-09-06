# -*- coding: utf-8 -*-

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose import Entry

import datetime

def reducer():
    pass

def line_to_entry(line):
    name, tail = line.split('\t')
    date, rank = tail.split(',')
    date = datetime.datetime.strptime(date, TP_TSTAMP_FORMAT)
    rank = int(rank)
    return Entry(name=name, date=date, rank=rank)
