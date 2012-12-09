# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm.exc import MultipleResultsFound

from midas.tests.test_crunchbase_crawler import COMPANIES_URL
from midas.tests.test_crunchbase_crawler import FOO_URL
from midas.tests.test_crunchbase_crawler import MEM_DB
from midas.tests.test_crunchbase_crawler import prepare_url_open
from midas.tests.test_crunchbase_crawler import unittest
from midas.crunchbase_crawler.model.db import Session
from midas.crunchbase_crawler.model.db import Base

import mock

TSTAMP = 'Tue Aug 07 22:57:25 UTC 2012'

class SqlTestCase(unittest.TestCase):

    def setUp(self):
        engine = create_engine(MEM_DB, echo=False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine, checkfirst=False)
        self.session = Session()

    def tearDown(self):
        Session.remove()

class FundingTests(SqlTestCase):

    def _get_target_class(self):
        from midas.crunchbase_crawler.model.db import FundingRound
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
        from midas.crunchbase_crawler.model.db import Company
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
        from midas.crunchbase_crawler.model.db import FundingRound
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
        self.assertEqual(len(c.funding_rounds), 2)
        result = self.session.query(self._get_target_class()).get(1)
        self.assertIs(result, c)
        self.assertEqual(len(result.funding_rounds), 2)

    def test_make_from_parsed_json_with_external_links(self):
        c = self._make_one_from_parsed_json(
            { 'external_links': [{'title': 'foo', 'external_url': 'blah'},
                                 {'title': 'bar', 'external_url': 'more_blah'}] })
        self.assertEqual(len(c.external_links), 2)
        self.assertEqual(c.external_links[0].title, 'foo')
        self.assertEqual(c.external_links[1].external_url, 'more_blah')
        result = self.session.query(self._get_target_class()).get(1)
        self.assertIs(result, c)
        self.assertEqual(len(result.external_links), 2)

    def test_funding_round_is_deleted_with_company(self):
        c = self._make_one_from_parsed_json(
            {'funding_rounds': [ {'funded_day': 30} ]})
        self.session.delete(c)
        from midas.crunchbase_crawler.model.db import FundingRound
        result = self.session.query(FundingRound).all()
        self.assertEqual(result, [])

    def test_query_url(self):
        c = self._make_one(permalink='foo')
        self.assertEqual(c.query_url(), FOO_URL)
    
    def test_str(self):
        c = self._make_one(permalink='foo')
        self.assertEqual(str(c), 'Company(foo)')

    @mock.patch('midas.crunchbase_crawler.model.urlopen')
    def test_update_when_company_fresh(self, urlopen):
        c = self._get_target_class()(permalink='foo')
        prepare_url_open(urlopen, {FOO_URL: {'description': 'blah',
                                             'updated_at': TSTAMP}})
        c.update()
        result = self.session.query(self._get_target_class()).one()
        self.assertEqual(result.description, 'blah')
        self.assertIsNot(c, result)

    @mock.patch('midas.crunchbase_crawler.model.urlopen')
    def test_update_when_company_persisted(self, urlopen):
        c = self._make_one(permalink='foo')
        prepare_url_open(urlopen, {FOO_URL: {'description': 'blah',
                                             'updated_at': TSTAMP}})
        c.update()
        urlopen.assert_called_once_with(FOO_URL)
        results = self.session.query(self._get_target_class()).all()
        self.assertEqual(len(results), 1)
        result = results.pop()
        self.assertEqual(result.description, 'blah')
        self.assertIsNot(c, result)


class DataBaseRootTests(unittest.TestCase):

    def test_companies_list_creation(self):
        from midas.crunchbase_crawler.model.db import DataBaseRoot
        root = DataBaseRoot(MEM_DB)
        cl = root.get('companies')
        from midas.crunchbase_crawler.model.db import CompanyList
        self.assertIsInstance(cl, CompanyList)


class CompanyListTests(SqlTestCase):

    def _make_one(self):
        from midas.crunchbase_crawler.model.db import CompanyList
        return CompanyList()

    @mock.patch('midas.crunchbase_crawler.model.urlopen')
    def test_update(self, urlopen):
        prepare_url_open(urlopen,
                         {COMPANIES_URL: [{'permalink': 'foo'}]})
        cl = self._make_one()
        cl.update()
        urlopen.assert_called_once_with(COMPANIES_URL)

    def test_get_on_new_company(self):
        cl = self._make_one()
        result = cl.get('foo')
        from midas.crunchbase_crawler.model.db import Company
        self.assertIsInstance(result, Company)
        self.assertEqual(str(result), 'Company(foo)')
        self.assertIsNone(result.id)

    def test_get_on_existent_company(self):
        cl = self._make_one()
        comp1 = cl.get('foo')
        self.session.add(comp1)
        comp2 = cl.get('foo')
        self.assertIs(comp1, comp2)

    @mock.patch('logging.critical')
    def test_duplicate_entries_raises_error(self, critical):
        cl = self._make_one()
        comp1 = cl.get('foo')
        comp2 = cl.get('foo')
        self.session.add(comp1)
        self.session.add(comp2)
        with self.assertRaises(MultipleResultsFound):
            cl.get('foo')
        critical.assert_called_once()

    def test_local_list_when_db_empty(self):
        cl = self._make_one()
        self.assertEqual(list(cl.list_local()), [])

    def test_local_list_with_elements(self):
        cl = self._make_one()
        self.session.add(cl.get('foo'))
        self.session.add(cl.get('bar'))
        result = list(map(str, cl.list_local()))
        result.sort()
        expected = [ 'Company({0})'.format(n) 
                     for n in ('bar', 'foo') ]
        self.assertEqual(result, expected)

    def test_list_not_local_wo_elements(self):
        cl = self._make_one()
        cl._remote_data = []
        result = list(cl.list_not_local())
        expected = []
        self.assertEqual(result, expected)

    def test_list_not_local_w_elements(self):
        cl = self._make_one()
        cl._remote_data = [{'permalink': 'foo'},
                           {'permalink': 'bar'}]
        result = list(map(str, cl.list_not_local()))
        result.sort()
        expected = [ 'Company({0})'.format(n) 
                     for n in ('bar', 'foo') ]
        self.assertEqual(result, expected)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
