# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

PY_VERSION = sys.version_info[:2]

if PY_VERSION == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

from midas import RankEntry
from vincetools.compat import StringIO


__here__ = os.path.abspath(os.path.dirname(__file__))
__test_data__ = os.path.join(__here__, 'data')
TEST_DATA = (os.path.join(__test_data__, 'top-1m-2012-09-03.csv.zip'),
             (RankEntry('foo', datetime.datetime(2012, 9, 3), 1),
              RankEntry('bar', datetime.datetime(2012, 9, 3), 2)))


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
