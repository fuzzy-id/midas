# -*- coding: utf-8 -*-

import argparse
import datetime
import logging
import os.path
import sys

from ev_transpose import TP_TSTAMP_FORMAT
from ev_transpose import Entry
from ev_transpose.compat import GzipFile
from ev_transpose.compat import ZipFile
from ev_transpose.compat import comp_bytes

TSTAMP_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

def main(argv=sys.argv):
    command = EvTranspose(argv)
    return command.run()

class EvTranspose(object):

    description = ""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('dst', help='the destination for the output files')
    parser.add_argument('zip_file', nargs='+', help='the zipped files to parse')
    
    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self.dst = self.args.dst

    def run(self):
        logging.basicConfig(level=logging.INFO)
        for zfile in self.args.zip_file:
            logging.info("Processing '{0}'".format(zfile))
            for entry in parse_input_file(zfile):
                self.write_out(entry)
        return 0

    def write_out(self, entry):
        with GzipFile(self.expand(entry.name), 'w') as fp:
            fp.write(comp_bytes(self.format_out(entry), 'utf-8'))

    def expand(self, fname):
        return os.path.join(self.dst, '.'.join((fname, 'gz')))

    def format_out(self, entry):
        date = entry.date.strftime(TP_TSTAMP_FORMAT)
        return '{e.name}, {0}, {e.rank}'.format(date, e=entry)


def parse_input_file(fname):
    date = convert_fname_to_tstamp(fname)
    for line in unzip_file(fname):
        rank, name = split_rank_name(line)
        yield Entry(name=name, rank=rank, date=date)

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

def convert_fname_to_tstamp(fname):
    fname_last = os.path.basename(fname)
    date = datetime.datetime.strptime(fname_last, TSTAMP_FORMAT)
    return date
