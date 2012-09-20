# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

PY_VERSION = sys.version_info[:2]

if PY_VERSION == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

from midas.compat import StringIO


class IntegrationTestCase(unittest.TestCase):

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
