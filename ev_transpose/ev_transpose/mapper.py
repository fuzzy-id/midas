# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import hashlib
import os.path
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose.compat import ZipFile

import hbase

TSTAMP_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

def mapper():
    for fname in sys.stdin:
        fname = fname.strip()
        print("Processing '{0}'".format(fname), file=sys.stderr)
        tstamp = convert_fname_to_tstamp(fname)
        for l in unzip_file(fname):
            rank, name = split_rank_name(l)
            domain_dot_tld = normalize_site(name)
            print(type(domain_dot_tld))
            h = hashlib.sha1(domain_dot_tld)
            h_start = h[:2]
            print("{0}\t{1}, {2}, {3}".format(h_start, name, tstamp, rank))
    return 0

def normalize_site(name):
    splits = name.split('/')
    if splits[0] == 'http:':
        assert splits[1] == ''
        host = splits[2]
    else:
        host = splits[0]
    splits = host.split('.')
    return '.'.join(splits[-2:])

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
