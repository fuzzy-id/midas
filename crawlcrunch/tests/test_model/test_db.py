# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import create_engine

from crawlcrunch.tests import MEM_DB
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest
from crawlcrunch.model.db import Session
from crawlcrunch.model.db import Base

import mock

TSTAMP = 'Tue Aug 07 22:57:25 UTC 2012'

class SqlTestCase(unittest.TestCase):

    def setUp(self):
        engine = create_engine(MEM_DB, echo=False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

    def tearDown(self):
        Session.remove()

class FundingTests(SqlTestCase):

    def _get_target_class(self):
        from crawlcrunch.model.db import FundingRound
        return FundingRound

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_id_gets_generated(self):
        f = self._make_one()
        self.assertIsNone(f.id)
        self.assertIsNone(f.funded_day)
        self.session.add(f)
        self.session.commit()
        self.assertIsNotNone(f.id)

    def test_instantiation_by_keywords(self):
        f = self._make_one(funded_day=80, funded_year=50)
        self.assertEqual(f.funded_day, 80)
        self.assertEqual(f.funded_year, 50)

    def test_instantiation_by_dict(self):
        f = self._make_one(**{'funded_day': 80,
                              'funded_year': 50})
        self.assertEqual(f.funded_day, 80)
        self.assertEqual(f.funded_year, 50)

    def test_with_not_available_keywords(self):
        with self.assertRaises(TypeError):
            self._make_one(foo='bar')
        with self.assertRaises(TypeError):
            self._make_one(**{'foo': 'bar'})

class CompanyTests(SqlTestCase):

    def _get_target_class(self):
        from crawlcrunch.model.db import Company
        return Company

    def _make_one(self, *args, **kwargs):
        c = self._get_target_class()(*args, **kwargs)
        self.session.add(c)
        self.session.commit()
        return c

    def _make_one_from_parsed_json(self, *args, **kwargs):
        c = self._get_target_class()\
            .make_from_parsed_json(*args, **kwargs)
        self.session.add(c)
        self.session.commit()
        return c

    def test_updated_at_is_datetime_when_from_parsed_json(self):
        c = self._make_one_from_parsed_json({'updated_at': TSTAMP})
        expected = datetime.datetime(2012, 8, 7, 22, 57, 25)
        self.assertEqual(c.updated_at, expected)
        
    def test_company_with_fundings_list(self):
        from crawlcrunch.model.db import FundingRound
        f1 = FundingRound(funded_year=40)
        f2 = FundingRound(funded_year=30)
        c = self._make_one(funding_rounds=[f1, f2])
        result = self.session.query(self._get_target_class()).get(1)
        self.assertIs(result, c)
        self.assertIs(result.funding_rounds[0], f1)
        self.assertIs(result.funding_rounds[1], f2)
        
    def test_make_from_parsed_json_with_fundings(self):
        c = self._make_one_from_parsed_json(
            { 'funding_rounds': [ {'funded_day': 30},
                                  {'round_code': 'angel'} ],
              'description': 'foo' } )
        result = self.session.query(self._get_target_class()).get(1)
        self.assertIs(result, c)
        self.assertEqual(len(result.funding_rounds), 2)

    def test_funding_round_is_deleted_with_company(self):
        c = self._make_one_from_parsed_json(
            {'funding_rounds': [ {'funded_day': 30} ]})
        self.session.delete(c)
        from crawlcrunch.model.db import FundingRound
        result = self.session.query(FundingRound).all()
        self.assertEqual(result, [])

    def test_query_url(self):
        c = self._make_one(name='foo')
        expected = 'http://api.crunchbase.com/v/1/company/foo.js'
        self.assertEqual(c.query_url(), expected)
    
    def test_str(self):
        c = self._make_one(name='foo')
        self.assertEqual(str(c), 'Company( foo )')

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_update(self, urlopen):
        c = self._make_one(name='foo')
        foo_url = 'http://api.crunchbase.com/v/1/company/foo.js'
        prepare_url_open(urlopen, {foo_url: {'description': 'blah',
                                             'updated_at': TSTAMP}})
        c.update()
        urlopen.assert_called_once_with(foo_url)
        results = self.session.query(self._get_target_class()).all()
        self.assertEqual(len(results), 1)
        result = results.pop()
        self.assertEqual(result.description, 'blah')
        self.assertIsNot(c, result)


class DataBaseRootTests(unittest.TestCase):

    def test_companies_list_creation(self):
        from crawlcrunch.model.db import DataBaseRoot
        root = DataBaseRoot(MEM_DB)
        cl = root.get('companies')
        from crawlcrunch.model.db import CompanyList
        self.assertIsInstance(cl, CompanyList)

class CompanyListTests(SqlTestCase):

    def _make_one(self):
        from crawlcrunch.model.db import CompanyList
        return CompanyList()

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_update(self, urlopen):
        url = 'http://api.crunchbase.com/v/1/companies.js'
        prepare_url_open(urlopen,
                         {url: [{'permalink': 'foo'}]})
        cl = self._make_one()
        cl.update()
        urlopen.assert_called_once_with(url)
