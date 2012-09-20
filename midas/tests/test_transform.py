# -*- coding: utf-8 -*-

import datetime
import os
import shutil
import sys
import tempfile

import mock

from midas import RankEntry
from midas.compat import StringIO
from midas.tests import TEST_DATA
from midas.tests import IntegrationTestCase

class AlexaToSha1Tests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.transform import run_alexa_to_sha1
        return run_alexa_to_sha1

    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')

    def test_on_test_data(self):
        ret_code = self._run('-q', TEST_DATA[0])
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal('\n'.join(e.format_w_key 
                                           for e in TEST_DATA[1]) + '\n')


class SortSha1Tests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.transform import run_sort_sha1
        return run_sort_sha1

    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')

    def test_on_test_data(self):
        a_date = datetime.date(1900, 1, 1)
        entries = (RankEntry('foo', a_date, 1),
                   RankEntry('foo', a_date, 2),
                   RankEntry('bar', a_date, 1),
                   RankEntry('bar', a_date, 2))
        try:
            tmpd = tempfile.mkdtemp()
            ret_code = self._run('-q', '-d', tmpd, 
                                 *( e.format_w_key for e in entries ))
            self.assertEqual(ret_code, 0)
            listing = os.listdir(tmpd)
            listing.sort()
            # foo -> 0b; bar -> 62
            self.assertEqual(listing, ['0b.gz', '62.gz']) 
        finally:
            shutil.rmtree(tmpd)
