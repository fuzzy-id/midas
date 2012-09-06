# -*- coding: utf-8 -*-

import collections
import datetime
import os.path
import sys

PY_VERSION = sys.version_info[:2]

if PY_VERSION == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

Entry = collections.namedtuple('Entry', ['name', 'date', 'rank'])

__here__ = os.path.abspath(os.path.dirname(__file__))
__test_data__ = os.path.join(__here__, 'data')
TEST_DATA = (
    (os.path.join(__test_data__, 'top-1m-2012-09-03.csv.zip', ),
     (Entry('foo', '2012-09-03', 1),
      Entry('bar', '2012-09-03', 2))), )
