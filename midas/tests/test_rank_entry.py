# -*- coding: utf-8 -*-

import datetime

from midas.compat import unittest
import midas.compat as vt_comp

from midas.tests import TEST_ALEXA_TOP1M
from midas.tests import TEST_ALEXA_TOP1M_FILES


class RankEntryTestCase(unittest.TestCase):

    a_date = datetime.datetime(1900, 1, 1)
    one_day = datetime.timedelta(days=1)

    def _get_target_cls(self):
        from midas import RankEntry
        return RankEntry

    def _make_one(self, site, date, rank):
        return self._get_target_cls()(site=site, date=date, rank=rank)

    def assert_lt_le_neq(self, lesser, greater):
        self.assertTrue(lesser <  greater)
        self.assertTrue(lesser <= greater)
        self.assertTrue(lesser != greater)
        self.assertTrue(greater != lesser)
        self.assertTrue(greater >= lesser)
        self.assertTrue(greater >  lesser)
        self.assertFalse(greater <  lesser)
        self.assertFalse(greater <= lesser)
        self.assertFalse(greater == lesser)
        self.assertFalse(lesser == greater)
        self.assertFalse(lesser >= greater)
        self.assertFalse(lesser >  greater)

    def test_str_representation(self):
        entry = self._make_one('foo', self.a_date, 1)
        self.assertEqual(str(entry), 'RankEntry(foo, 1900-01-01, 1)')

    def test_cmp_different_names_remaining_same(self):
        a = self._make_one('bar', self.a_date, 1)
        b = self._make_one('foo', self.a_date, 1)
        self.assert_lt_le_neq(a, b)

    def test_cmp_different_names_and_dates(self):
        a = self._make_one('bar', self.a_date + self.one_day, 1)
        b = self._make_one('foo', self.a_date, 1)
        self.assert_lt_le_neq(a, b)

    def test_cmp_different_names_and_ranks(self):
        a = self._make_one('bar', self.a_date, 2)
        b = self._make_one('foo', self.a_date, 1)
        self.assert_lt_le_neq(a, b)

    def test_cmp_different_names_dates_and_ranks(self):
        a = self._make_one('bar', self.a_date + self.one_day, 2)
        b = self._make_one('foo', self.a_date, 1)
        self.assert_lt_le_neq(a, b)

    def test_cmp_different_dates_remaining_same(self):
        a = self._make_one('bar', self.a_date, 1)
        b = self._make_one('bar', self.a_date + self.one_day, 1)
        self.assert_lt_le_neq(a, b)

    def test_cmp_different_dates_and_ranks(self):
        a = self._make_one('bar', self.a_date, 2)
        b = self._make_one('bar', self.a_date + self.one_day, 1)
        self.assert_lt_le_neq(a, b)

    def test_cmp_different_ranks(self):
        a = self._make_one('bar', self.a_date, 1)
        b = self._make_one('bar', self.a_date, 2)
        self.assert_lt_le_neq(a, b)

    def test_cmp_sort_a_list(self):
        a = self._make_one('foo', self.a_date, 2)
        b = self._make_one('foo', self.a_date + self.one_day, 1)
        c = self._make_one('foo', self.a_date + self.one_day*2, 1)
        d = self._make_one('foo', self.a_date + self.one_day*3, 1)
        entries = [d, b, a, c]
        entries.sort()
        self.assertEqual(entries, [a, b, c, d])

    def test_iter_example_alexa_file(self):
        result = [ e
                   for f in TEST_ALEXA_TOP1M_FILES 
                   for e in self._get_target_cls().iter_alexa_file(f) ]
        self.assertEqual(result, TEST_ALEXA_TOP1M)

    def test_format_and_parse_json(self):
        a = self._make_one('foo', self.a_date, 2)
        cls = self._get_target_cls()
        b = cls.parse_json(a.format_json)
        self.assertIsNot(a, b)
        self.assertEqual(a, b)
