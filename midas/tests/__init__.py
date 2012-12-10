# -*- coding: utf-8 -*-

import datetime
import os.path
import sys

from midas import RankEntry
from midas.tools import SiteCount
from vincetools.compat import StringIO
from vincetools.compat import unittest

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


class ConfiguredDBTestCase(unittest.TestCase):

    companies_js = [{'name': 'foo',
                     'homepage_url': 'http://foo.example.com/path',
                     'funding_rounds': [{'funded_year': 2012,
                                         'funded_month': 10,
                                         'funded_day': 2,
                                         'round_code': 'seed'},
                                        {'funded_year': 2011,
                                         'funded_month': 1,
                                         'funded_day': 1,
                                         'round_code': 'angel'}]},
                    {'name': 'baz-bar',
                     'homepage_url': 'http://baz.bar.example.com/'}]

    def setUp(self):
        import midas.config as md_cfg
        import midas.db as md_db
        md_cfg.read_string(TEST_CONFIG)
        self.session = md_db.db_session()

    def tearDown(self):
        from crawlcrunch.model.db import Session
        import midas.db as md_db
        import midas.config as md_cfg
        md_db.Session.remove()
        md_db._session = None
        md_cfg.new_configparser()
        
    def _make_company_json(self, js):
        from midas.db import Company
        c = Company.make_from_parsed_json(js)
        self._add_to_db(c)
        return c

    def _add_to_db(self, obj):
        self.session.add(obj)
        self.session.commit()
