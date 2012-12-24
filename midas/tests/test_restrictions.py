# -*- coding: utf-8 -*-

import datetime

import pandas

from midas.compat import unittest

class MeanRankInRangeAtDateTests(unittest.TestCase):

    def _make_one(self, *args, **kwargs):
        from midas.restrictions import MeanRankInRangeAtDate
        return MeanRankInRangeAtDate(*args, **kwargs)

    def test_fulfill(self):
        restr = self._make_one(datetime.date(2012, 12, 24), 10, 12)
        s = pandas.Series([8, 11, 15], pandas.date_range('2012-12-22', '2012-12-24'))
        self.assertTrue(restr.fulfills(s))
        s = pandas.Series([13, 11, 15], pandas.date_range('2012-12-22', '2012-12-24'))
        self.assertFalse(restr.fulfills(s))
        s = pandas.Series([8, 11, 15], pandas.date_range('2010-12-22', '2010-12-24'))
        self.assertFalse(restr.fulfills(s))

    def test_zero_days_offset(self):
        restr = self._make_one(datetime.date(2012, 12, 24), 10, 12, 
                               pandas.DateOffset(0))
        s = pandas.Series([8, 11, 12], pandas.date_range('2012-12-22', '2012-12-24'))
        self.assertTrue(restr.fulfills(s))
        s = pandas.Series([13, 11, 15], pandas.date_range('2012-12-22', '2012-12-24'))
        self.assertFalse(restr.fulfills(s))
        s = pandas.Series([8, 11, 15], pandas.date_range('2010-12-22', '2010-12-24'))
        self.assertFalse(restr.fulfills(s))
