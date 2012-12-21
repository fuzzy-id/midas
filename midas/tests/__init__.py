# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

from midas import RankEntry
from midas.tools import SiteCount
from midas.compat import StringIO
from midas.compat import unittest

_here = os.path.abspath(os.path.dirname(__file__))
_test_data_home = os.path.join(_here, 'data')

TEST_CONFIG = """
[location]
data_home = {0}
crunchbase_db = sqlite:///:memory:
""".format(_test_data_home)

TEST_ALEXA_TOP1M_FILES = [
    os.path.join(_test_data_home, 'alexa_zip_files', 'top-1m-2012-09-03.csv.zip'),
    os.path.join(_test_data_home, 'alexa_zip_files', 'top-1m-2012-09-04.csv.zip'),
    ]

TEST_ALEXA_TOP1M = [
    RankEntry('foo.example.com', 
              datetime.datetime(2012, 9, 3), 
              1),
    RankEntry('baz.bar.example.com/path', 
              datetime.datetime(2012, 9, 3), 
              2),
    RankEntry('baz.bar.example.com/path', 
              datetime.datetime(2012, 9, 4), 
              1),
    ]

TEST_SITE_COUNT = [
    SiteCount('foo.example.com', 1),
    SiteCount('baz.bar.example.com/path', 2)
    ]
