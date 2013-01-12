# -*- coding: utf-8 -*-

import os.path
import shelve

import pandas

from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import IntegrationTestCase

class Tests(IntegrationTestCase):

    def _get_target_cls(self):
        from midas.scripts.sample_restriction import MakeSampleRestrictionShelve
        return MakeSampleRestrictionShelve

    def test_on_test_data(self):
        shelf = os.path.join(self.tmpd, 'shelf')
        self.assertEqual(
            self._call_cmd(shelf, TEST_DATA_PATH['sites_w_company']),
            0
            )
        d = shelve.open(shelf)
        self.assertEqual(len(d), 1)
        self.assertTrue(d.has_key('foo'))
        restr = d['foo']
        self.assertEqual(restr.site, 'foo.example.com')
        self.assertEqual(restr.tstamp, pandas.Timestamp('2012-09-03'))
        self.assertEqual(restr.date_lower, pandas.Timestamp('2012-08-31'))
        self.assertEqual(restr.date_upper, pandas.Timestamp('2012-09-06'))
        self.assertEqual(restr.rank_lower, 0)
        self.assertEqual(restr.rank_upper, 2)
