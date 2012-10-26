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


class ConfiguredDBTestCase(unittest.TestCase):

    companies_js = [{'name': 'foo',
                     'homepage_url': 'http://foo.example.com/path',
                     'funding_rounds': [{'funded_year': 2012,
                                         'round_code': 'seed'},
                                        {'funded_year': 2011,
                                         'round_code': 'angel'}]},
                    {'name': 'baz-bar',
                     'homepage_url': 'http://baz.bar.example.com/'}]

    def setUp(self):
        from crawlcrunch.model.db import Base
        from crawlcrunch.model.db import Session
        from crawlcrunch.model.db import create_engine
        import midas.config as md_cfg
        import midas.db as md_db
        engine = create_engine('sqlite:///:memory:')
        Session.configure(bind=engine)
        Base.metadata.create_all(engine, checkfirst=False)
        self.session = Session()
        md_db._session = self.session
        md_cfg.read_string(TEST_CONFIG)

    def tearDown(self):
        from crawlcrunch.model.db import Session
        import midas.db as md_db
        import midas.config as md_cfg
        Session.remove()
        md_db._session = None
        md_cfg.new_configparser()
        
    def _make_company_json(self, js):
        from crawlcrunch.model.db import Company
        c = Company.make_from_parsed_json(js)
        self.session.add(c)
        return c
