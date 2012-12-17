#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import shelve
import random
import restrictions

import pig_schema

SHELVE_FILE = 'a_shelve'

OUT_TUPLE = collections.namedtuple('Tuple', 'site company tstamp')

@pig_schema.pig_input(
    '(site:chararray, ranking{(tstamp:chararray, rank:int)})'
    )
@pig_schema.pig_output(
    '(site:chararray, company: chararray, tstamp: chararray)'
    )
def main(field):
    series = pandas.Series(dict((pandas.Timestamp(d), r))
                           for d, r in field.ranking)
    random.shuffle(RESTRICTIONS)
    for company, restriction in RESTRICTIONS:
        if restriction.fulfills(company):
            yield OUT_TUPLE(field.site, company, restriction.tstamp)
            break
