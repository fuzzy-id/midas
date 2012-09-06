# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

from ev_transpose import split_rank_name
from ev_transpose import unzip_file

TSTAMP_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

def mapper():
    for fname in sys.stdin:
        fname_last = os.path.basename(fname)
        date = datetime.datetime.strptime(fname_last, TSTAMP_FORMAT)
        tstamp = date.strftime('%Y-%m-%d')
        for l in unzip_file(fname):
            rank, name = split_rank_name(l)
            print('{0}\t{1}, {2}'.format(name, tstamp, rank))
    return 0

def reducer():
    pass
