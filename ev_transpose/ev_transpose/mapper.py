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
    con = hbase.HBConnection('localhost', '50080')
    tbl = con['alexa-top-1m']
    print(tbl.schema, file=sys.stderr)
    for fname in sys.stdin:
        fname = fname.strip()
        print("Processing '{0}'".format(fname), file=sys.stderr)
        tstamp = convert_fname_to_tstamp(fname)
        column = 'ts:{0}'.format(tstamp)
        for i, l in enumerate(unzip_file(fname)):
            rank, name = split_rank_name(l)
            row = hbase.Row(name, [hbase.Cell(str(rank), column)])
            tbl.update(row)
            if i % 1000 == 0:
                print("Processed {0} entries".format(i), file=sys.stderr)
    return 0

def convert_fname_to_tstamp(fname):
    date = convert_fname_to_date(fname)
    return date.strftime(TP_TSTAMP_FORMAT)

def convert_fname_to_date(fname):
    fname_last = os.path.basename(fname)
    return datetime.datetime.strptime(fname_last, TSTAMP_FORMAT)

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
