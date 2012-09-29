# -*- coding: utf-8 -*-

import argparse
import itertools
import logging
import operator
import sys

from midas import RankEntry
from midas.compat import imap

def run_alexa_to_names_and_one(argv=sys.argv):
    cmd = AlexaToNamesAndOne(argv)
    cmd.run()
    return 0

class AlexaToNamesAndOne(object):
    """ Parse Alexa Top1M files and print the names found in the
    entries as key and a `1' as value.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', dest='verbosity', 
                        action='append_const', const=-10, 
                        help='be verbose, can be given multiple times',
                        default=[logging.getLevelName('INFO')])
    parser.add_argument('-q', '--quiet', dest='verbosity', 
                        action='append_const', const=10,
                        help='be quiet, can be given multiple times')
    parser.add_argument('stream', nargs='*', metavar='FILE', default=sys.stdin,
                        help='the files to read')

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self.args.verbosity = sum(self.args.verbosity)
        logging.basicConfig(level=self.args.verbosity, stream=sys.stderr)

    def run(self):
        for fname in self.args.stream:
            logging.info("processing '{0}'".format(fname))
            for entry in RankEntry.iter_alexa_file(fname):
                print("{0}\t1".format(entry.name))

def run_sum_names(argv=sys.argv):
    cmd = SumValues(argv)
    cmd.run()
    return 0

class SumValues(object):
    """ Sums up the counts of the keys.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', dest='verbosity',
                        action='append_const', const=-10,
                        help='be verbose, can be given multiple times',
                        default=[logging.getLevelName('INFO')])
    parser.add_argument('-q', '--quiet', dest='verbosity',
                        action='append_const', const=10,
                        help='be quiet, can be given multiple times')
    parser.add_argument('stream', nargs='*', metavar='FILE', default=sys.stdin,
                        help='the records to read')

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self.args.verbosity = sum(self.args.verbosity)
        logging.basicConfig(level=self.args.verbosity, stream=sys.stderr)

    def run(self):
        for block in get_in_blocks(self.args.stream):
            counter = 0
            for entry in block:
                name_tab_count = entry.strip()
                name, count = name_tab_count.split('\t')
                counter += int(count)
            print('{0}\t{1}'.format(name, counter))

def get_in_blocks(iterable, key_value_sep='\t'):
    keyfunc = lambda entry: entry.split(key_value_sep, 1)[0]
    return imap(operator.itemgetter(1), itertools.groupby(iterable, keyfunc))
