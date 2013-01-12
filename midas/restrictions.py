# -*- coding: utf-8 -*-
""" As we need to pickle and unpickle the instances of these classes they 
have to go in their own module.
"""

import numpy
import pandas

class MeanRankInRangeAtDate(object):

    def __init__(self, site, date, rank_lower, rank_upper, 
                 date_offset=pandas.DateOffset(days=3)):
        self.site = site
        self.tstamp = date
        self.date_lower = date - date_offset
        self.date_upper = date + date_offset
        self.rank_lower = rank_lower
        self.rank_upper = rank_upper

    def fulfills(self, ts):
        mean = ts[self.date_lower:self.date_upper].median()
        return (not numpy.isnan(mean)  
                and (self.rank_lower <= mean <= self.rank_upper))

