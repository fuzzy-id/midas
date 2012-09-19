# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

PY_VERSION = sys.version_info[:2]

if PY_VERSION == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

from ev_transpose import Entry
from ev_transpose.compat import StringIO


__here__ = os.path.abspath(os.path.dirname(__file__))
__test_data__ = os.path.join(__here__, 'data')
TEST_DATA = (
    (os.path.join(__test_data__, 'top-1m-2012-09-03.csv.zip', ),
     (Entry('foo', '2012-09-03', 1),
      Entry('bar', '2012-09-03', 2))), )


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self._oldout = sys.stdout
        sys.stdout = StringIO()
        self._oldin = sys.stdin
        sys.stdin = StringIO()

    def tearDown(self):
        sys.stdout = self._oldout
        sys.stdin = self._oldin
