# -*- coding: utf-8 -*-

import functools
import itertools
import logging
import operator

from midas import MDCommand
from midas import RankEntry
from midas.compat import ifilter
from midas.compat import imap
from midas.compat import urlparse


VALID_CHRS = set(chr(i)
                 for i in itertools.chain(range(ord('a'), ord('z') + 1),
                                          range(ord('A'), ord('Z') + 1),
                                          range(ord('0'), ord('9') + 1),
                                          (ord(c) for c in ('-', '.', '_'))))

def count_entries(iterable):
    try:
        return len(iterable)
    except TypeError:
        counter = 0
        for _ in iterable:
            counter += 1
        return counter

def num_dots(name):
    eq_dot = functools.partial(operator.eq, '.')
    return count_entries(ifilter(eq_dot, name))

def is_ip_adress(name):
    last = name.split('.')[-1]
    try:
        int(last)
        return True
    except ValueError:
        return False

def is_valid_name(name):
    for n in name:
        if n not in VALID_CHRS:
            return False
    return True

def is_invalid_name(name):
    return not is_valid_name(name)

def filter_invalid_names(names):
    return ifilter(is_invalid_name, names)

def group_by_key(iterable, sep='\t'):
    keyfunc = functools.partial(key, sep=sep)
    return imap(operator.itemgetter(1), itertools.groupby(iterable, keyfunc))

def key(line, sep='\t'):
    return split_key_value(line, sep)[0]

def split_key_value(line, sep='\t'):
    return line.strip().split(sep, 1)

def cut_www(s):
    if s.startswith('www.'):
        return s[4:]
    return s

def netloc(url):
    return urlparse(url).netloc

class AlexaToNamesAndOne(MDCommand):
    """ Parse Alexa Top1M files and print the names found in the
    entries as key and a `1' as value.
    """

    def run(self):
        for fname in self.args.stream:
            logging.info("processing '{0}'".format(fname))
            for entry in RankEntry.iter_alexa_file(fname):
                print("{0}\t1".format(entry.name))


class SumValues(MDCommand):
    """ Sums up the counts of the keys.
    """

    def run(self):
        for group in group_by_key(self.args.stream):
            counter = 0
            for entry in group:
                name_tab_count = entry.strip()
                name, count = name_tab_count.split('\t')
                counter += int(count)
            print('{0}\t{1}'.format(name, counter))
