# -*- coding: utf-8 -*-

import datetime

from midas.tests import unittest
from midas.tests import TEST_DATA

class RankEntryTestCase(unittest.TestCase):

    def _get_target_cls(self):
        from midas import RankEntry
        return RankEntry


class FormatTests(RankEntryTestCase):

    def _make_one(self, name, date, rank):
        return self._get_target_cls()(name=name, date=date, rank=rank)

    def test_format_std(self):
        entry = self._make_one('foo', datetime.datetime(1900, 1, 1), 1)
        self.assertEqual(entry.format_std, 'foo\t1900-01-01, 1')

    def test_format_w_key(self):
        entry = self._make_one('foo', datetime.datetime(1900, 1, 1), 1)
        self.assertEqual(entry.format_w_key, '0b\tfoo\t1900-01-01, 1')


class IterAlexaFileTests(RankEntryTestCase):

    def test_on_example_data(self):
        result = tuple(self._get_target_cls().iter_alexa_file(TEST_DATA[0]))
        self.assertEqual(result, TEST_DATA[1])
