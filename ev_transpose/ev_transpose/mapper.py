# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose.compat import ZipFile

TSTAMP_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

def mapper():
    for fname in sys.stdin:
        fname = fname.strip()
        tstamp = convert_fname_to_tstamp(fname)
        for l in unzip_file(fname):
            rank, name = split_rank_name(l)
            print('{0}\t{1}, {2}'.format(name, tstamp, rank))
    return 0

def convert_fname_to_tstamp(fname):
    fname_last = os.path.basename(fname)
    date = datetime.datetime.strptime(fname_last, TSTAMP_FORMAT)
    return date.strftime(TP_TSTAMP_FORMAT)


def unzip_file(fname, filelist=('top-1m.csv', )):
    ''' Iterates over the compressed file.
    '''
    with ZipFile(fname) as zf:
        for zipped_file in filelist:
            for line in zf.open(zipped_file):
                yield line.decode().strip()

def split_rank_name(line):
    rank, name = line.split(',')
    return int(rank), name
