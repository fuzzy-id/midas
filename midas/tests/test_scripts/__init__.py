# -*- coding: utf-8 -*-

import sys

from vincetools.compat import StringIO
from vincetools.compat import unittest


class IntegrationTestCase(unittest.TestCase):

    def _run_it(self, *args):
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
