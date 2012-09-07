# -*- coding: utf-8 -*-

import argparse
import os.path
import sys

from ev_transpose import TP_TSTAMP_FORMAT

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
        for zfile in self.args.zip_file:
            with InputFile(zfile) as in_f:
                for entry in in_f:
                    self.write_out(entry)
        return 0

    def write_out(self, entry):
        with GzipFile(self.expand(entry.name), 'w') as fp:
            fp.write(self.format_out(entry))

    def expand(self, fname):
        return os.path.join(self.dst, '.'.join((fname, 'gz')))

    def format_out(self, entry):
        date = entry.date.strftime(TP_TSTAMP_FORMAT)
        return '{0}, {1}'.format(date, entry.rank)
