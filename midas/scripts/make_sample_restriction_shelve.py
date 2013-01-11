# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
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

from midas.scripts import MDCommand

SCHEMA = pig_schema.pig_schema_to_py_struct(
    ','.join(['(site: chararray',
              'ranking: bag{(tstamp: chararray, rank: int)}',
              'company: chararray',
              'code: chararray',
              'tstamp: chararray)'])
    )
PARSER = pig_schema.make_parser(SCHEMA)

ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument('files', metavar='FILE', nargs='+', 
                       help='The `sites_w_company` files to extract restrictions from.')

DATE_INTERVAL = pandas.DateOffset(days=3)
OFFSET = pandas.DateOffset(days=90)

def get_median_rank_at_funding_date(field):
    fund_date = pandas.Timestamp(field.tstamp) - OFFSET
    s = pandas.Series(dict((pandas.Timestamp(d), r)
                           for d, r in field.ranking))
    r = s[fund_date-DATE_INTERVAL:fund_date+DATE_INTERVAL].median()
    return fund_date, r

def main(iterator):
    for i in iterator:
        field = PARSER(i)
        fund_date, mean_rank = get_median_rank_at_funding_date(field)
        if numpy.isnan(mean_rank):
            continue
        mean_rank = int(mean_rank)
        border = int(2 ** math.log(mean_rank))
        restr = MeanRankInRangeAtDate(fund_date, 
                                      mean_rank - border,
                                      mean_rank + border)
        SHELF[field.company] = restr
        

if __name__ == '__main__':
    args = ARGPARSER.parse_args()
    SHELF = shelve.open('restrictions_shelve')
    main(fileinput.input(args.files))
    SHELF.sync()
    SHELF.close()

