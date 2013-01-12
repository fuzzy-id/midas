# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
import math
import shelve

import numpy
import pandas

from midas.pig_schema import SITES_W_COMPANY_PARSER
from midas.restrictions import MeanRankInRangeAtDate
from midas.scripts import MDCommand
from midas.scripts import StoreSingleFileOrDirectoryAction

DATE_INTERVAL = pandas.DateOffset(days=3)
OFFSET = pandas.DateOffset(days=90)

def get_median_rank_at_funding_date(field):
    fund_date = pandas.Timestamp(field.tstamp) - OFFSET
    s = pandas.Series(dict((pandas.Timestamp(d), r)
                           for d, r in field.ranking))
    r = s[fund_date-DATE_INTERVAL:fund_date+DATE_INTERVAL].median()
    return fund_date, r

class MakeSampleRestrictionShelve(MDCommand):

    def add_argument(self):
        self.parser.add_argument(
            'shelf',
            help='The file-name of the shelve.'
            )
        self.parser.add_argument(
            'sites_w_company', action=StoreSingleFileOrDirectoryAction,
            help='The directory or file where sites_w_company data resides.'
            )

    def run(self):
        shelf = shelve.open(self.args.shelf)
        for i in self.args.sites_w_company:
            field = SITES_W_COMPANY_PARSER(i)
            fund_date, mean_rank = get_median_rank_at_funding_date(field)
            if numpy.isnan(mean_rank):
                continue
            mean_rank = int(mean_rank)
            border = int(2 ** math.log(mean_rank))
            restr = MeanRankInRangeAtDate(fund_date, 
                                          mean_rank - border,
                                          mean_rank + border)
            shelf[field.company] = restr
        shelf.sync()
        shelf.close()
