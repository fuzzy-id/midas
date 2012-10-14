# -*- coding: utf-8 -*-

import datetime
import os
import random
import shutil
import sys
import tempfile

import mock

from vincetools.compat import GzipFile
from vincetools.compat import StringIO
from vincetools.compat import unittest

from midas import RankEntry
from midas.tests import SITE_COUNT
from midas.tests import TEST_CONFIG
from midas.tests import TEST_DATA
from midas.tests import IntegrationTestCase

class AlexaToKeyTests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.alexa_to_key_files import AlexaToKey
        return AlexaToKey.cmd

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


class KeyToFilesTests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.alexa_to_key_files import KeyToFiles
        return KeyToFiles.cmd

    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')

    @mock.patch('midas.hdfs.get_hadoop_exec')
    def test_on_test_data(self, hadoop_bin):
        a_date = datetime.date(1900, 1, 1)
        one_day = datetime.timedelta(days=1)
        foos = (RankEntry('foo', a_date, 2),
                RankEntry('foo', a_date + one_day, 1),
                RankEntry('foo', a_date + one_day*2, 1),
                RankEntry('foo', a_date + one_day*3, 1))
        bars = (RankEntry('bar', a_date, 2),
                RankEntry('bar', a_date + one_day, 1),
                RankEntry('bar', a_date + one_day*2, 1),
                RankEntry('bar', a_date + one_day*5, 1))
        in_foos = list(foos)
        random.shuffle(in_foos)
        in_bars = list(bars)
        random.shuffle(in_bars)
        hadoop_bin.return_value = 'echo'
        tmpd = tempfile.mkdtemp()
        try:
            with mock.patch('midas.scripts.alexa_to_key_files.tempfile.mkdtemp') as mkdtemp:
                mkdtemp.return_value = tmpd
                with mock.patch('midas.scripts.alexa_to_key_files.shutil.rmtree') as rmtree:
                    ret_code = self._run('-q', '-d', tmpd, 
                                         *( e.format_w_key for e in in_foos + in_bars ))
                    rmtree.assert_called_with(tmpd)
            self.assertEqual(ret_code, 0)
            listing = os.listdir(tmpd)
            listing.sort()
            # foo -> 0be; bar -> 62c
            self.assertEqual(listing, ['0be.gz', '62c.gz']) 
            with GzipFile(os.path.join(tmpd, '0be.gz')) as fp:
                self.assertEqual(fp.readlines(), [ (l.format_std + '\n').encode()
                                                   for l in foos ])
            with GzipFile(os.path.join(tmpd, '62c.gz')) as fp:
                self.assertEqual(fp.readlines(), [ (l.format_std + '\n').encode()
                                                   for l in bars ])
        finally:
            shutil.rmtree(tmpd)

class CheckTests(unittest.TestCase):

    def setUp(self):
        import midas.config as md_cfg
        md_cfg.read_string(TEST_CONFIG)

    def tearDown(self):
        import midas.config as md_cfg
        md_cfg.new_configparser()

    def test_check_and_calc_stats(self):
        from midas.scripts.alexa_to_key_files \
            import check_and_calc_mean_max_min_deviation_variance
        result = check_and_calc_mean_max_min_deviation_variance()
        self.assertEqual(result, (2, 2, 2, 0, 0))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
