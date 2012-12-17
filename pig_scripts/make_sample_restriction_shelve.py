#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
import fileinput
import math
import os
import os.path
import shelve
import sys

import numpy
import pandas

import pig_schema

from restrictions import MeanRankInRangeAtDate

SCHEMA = pig_schema.pig_schema_to_py_struct(
    ','.join(['(site: chararray',
              'ranking: bag{(tstamp: chararray, rank: int)}',
              'company: chararray',
              'code: chararray',
              'tstamp: chararray)'])
    )
PARSER = pig_schema.make_parser(SCHEMA)
FILES = '/data0/sites_w_company'

DATE_INTERVAL = pandas.DateOffset(days=3)
OFFSET = pandas.DateOffset(days=90)

def main(iterator):
    for i in iterator:
        field = PARSER(i)
        fund_date = pandas.Timestamp(field.tstamp) - OFFSET
        s = pandas.Series(dict((pandas.Timestamp(d), r)
                               for d, r in field.ranking))
        mean_rank = s[fund_date-DATE_INTERVAL:fund_date+DATE_INTERVAL].median()
        if numpy.isnan(mean_rank):
            continue
        mean_rank = int(mean_rank)
        border = int(2 ** math.log(mean_rank))
        restr = MeanRankInRangeAtDate(fund_date, 
                                      mean_rank - border,
                                      mean_rank + border)
        SHELF[field.company] = restr
        

if __name__ == '__main__':
    if os.path.isdir(FILES):
        FILES = [ os.path.join(FILES, f) for f in os.listdir(FILES) ]
    SHELF = shelve.open('restrictions_shelve')
    main(fileinput.input(FILES))
    SHELF.sync()
    SHELF.close()

