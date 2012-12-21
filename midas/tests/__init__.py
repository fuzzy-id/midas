# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

from midas import RankEntry
from midas.tools import SiteCount
from midas.compat import StringIO
from midas.compat import unittest

_here = os.path.abspath(os.path.dirname(__file__))
_test_data_home = os.path.join(_here, '..', '..', 'test_data')

TEST_DATA_PATH = {
    'alexa_zip_files': os.path.join(_test_data_home, 'alexa_zip_files'),
    'alexa_files': os.path.join(_test_data_home, 'alexa_files'),
    }
