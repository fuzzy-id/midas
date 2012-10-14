# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

from midas import RankEntry
from vincetools.compat import StringIO
from vincetools.compat import unittest

_here = os.path.abspath(os.path.dirname(__file__))
_test_data_home = os.path.join(_here, 'data')

TEST_CONFIG = """
[location]
home = {0}
key_length = 3
""".format(_test_data_home)

TEST_DATA = (os.path.join(_test_data_home, 'alexa_files', 
                          'top-1m-2012-09-03.csv.zip'),
             (RankEntry('foo', datetime.datetime(2012, 9, 3), 1),
              RankEntry('bar', datetime.datetime(2012, 9, 3), 2)))
SITE_COUNT = (os.path.join(_test_data_home, 'site_count.gz'),
              (('foo.example.com', 1),
               ('bar.example.com/path', 2)))


class IntegrationTestCase(unittest.TestCase):

    def _run(self, *args):
        effargs = ['script_name']
        effargs.extend(args)
        return self._get_target_func()(effargs)
        
    def setUp(self):
        self._oldout = sys.stdout
        sys.stdout = StringIO()
        self._oldin = sys.stdin
        sys.stdin = StringIO()

    def tearDown(self):
        sys.stdout = self._oldout
        sys.stdin = self._oldin

    def assert_stdout_startswith(self, s):
        sys.stdout.seek(0)
        val = sys.stdout.getvalue()
        self.assertTrue(val.startswith(s))

    def assert_stdout_equal(self, s):
        sys.stdout.seek(0)
        val = sys.stdout.getvalue()
        self.assertEqual(val, s)
