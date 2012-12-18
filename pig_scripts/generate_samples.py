#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import shelve
import random
import restrictions
import sys

import pandas

import pig_schema

SHELVE_FILE = 'restrictions_shelve'

OUT_TUPLE = collections.namedtuple('Tuple', 'site company tstamp')

@pig_schema.pig_output(
    '(site:chararray, company: chararray, tstamp: chararray)'
    )
@pig_schema.pig_input(
    '(site:chararray, ranking: bag{(tstamp:chararray, rank:int)})'
    )
def main(field):
    if len(RESTRICTIONS) > 0:
        series = pandas.Series(dict((pandas.Timestamp(d), r)
                                    for d, r in field.ranking))
        for i, (company, restriction) in enumerate(RESTRICTIONS):
            if restriction.fulfills(series):
                RESTRICTIONS.pop(i)
                out = OUT_TUPLE(field.site, 
                                company, 
                                restriction.tstamp.date().isoformat())
                yield out
                break

if __name__ == '__main__':
    SHELF = shelve.open(SHELVE_FILE)
    RESTRICTIONS = SHELF.items()
    random.shuffle(RESTRICTIONS)
    SHELF.close()
    main(sys.stdin)
