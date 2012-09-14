# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import os.path
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose.compat import ZipFile

import hbase

TSTAMP_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

def mapper():
    con = hbase.HBConnection('localhost', '8080')
    tbl = con['alexa-top-1m']
    for fname in sys.stdin:
        fname = fname.strip()
        print("Processing '{0}'".format(fname), file=sys.stderr)
        tstamp = convert_fname_to_tstamp(fname)
        column = 'ts:{0}'.format(tstamp)
        for l in unzip_file(fname):
            rank, name = split_rank_name(l)
            row = hbase.Row(name, [hbase.Cell(str(rank), column)])
            tbl.update(row)
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
    rank, name = line.split(',', 1)
    return int(rank), name
