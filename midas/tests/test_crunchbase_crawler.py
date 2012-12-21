# -*- coding: utf-8 -*-

from io import BytesIO

import json
import os
import os.path
import shutil
import tempfile
import threading

import mock

from midas.compat import GzipFile
from midas.compat import HTTPError
from midas.compat import StringIO
from midas.compat import unittest

from midas.tests import COMPANIES_URL
from midas.tests import EXAMPLES_PATH
from midas.tests import FOO_URL
from midas.tests import DummyCompany
from midas.tests import DummyCompanyList
from midas.tests import DummyRoot
from midas.tests import prepare_url_open


class UpdaterTests(unittest.TestCase):

    def test_update_on_companies_list_is_called(self):
        from midas.crunchbase_crawler import Updater
        dcl = DummyCompanyList()
        dcl.list_not_local.return_value = []
        updater = Updater(dcl)
        updater.run()
        dcl.update.assert_called_once_with()


class FetcherBehaviourOnErrorTests(unittest.TestCase):

    def _test_it(self, company):
        from midas.crunchbase_crawler import Fetcher
        semaphore = mock.MagicMock()
        cf = Fetcher(company, semaphore)
        cf.run()
        return cf, semaphore

    @mock.patch('logging.critical')
    def test_semaphore_is_released_on_error(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = Exception()
        _, semaphore = self._test_it(dc)
        semaphore.release.assert_called_once_with()
        critical.assert_called_once()

    @mock.patch('logging.critical')
    def test_404_is_properly_handled(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 404, 'Not Found', None, None)
        _, semaphore = self._test_it(dc)
        critical.assert_has_calls([])
        critical.assert_called_once()
        semaphore.release.assert_called_once_with()

    @mock.patch('logging.exception')
    def test_not_404_is_logged(self, exc):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 400, None, None, None)
        _, semaphore = self._test_it(dc)
        dc.update.assert_called_once()
        exc.assert_called_once()
        semaphore.release.assert_called_once_with()

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_504_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 504, None, None, None)
        _, semaphore = self._test_it(dc)
        dc.update.assert_called_once()
        exc.assert_called_once()
        self.assertEqual(critical.call_count, 2)
        self.assertEqual(semaphore.release.call_count, 3)

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_503_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 503, None, None, None)
        _, semaphore = self._test_it(dc)
        dc.update.assert_called_once()
        exc.assert_called_once()
        self.assertEqual(critical.call_count, 2)
        self.assertEqual(semaphore.release.call_count, 3)


class LocalFilesRootTests(unittest.TestCase):

    def _make_one(self, path):
        from midas.crunchbase_crawler import LocalFilesRoot
        return LocalFilesRoot(path)

    def test_companies_list_creation(self):
        from midas.crunchbase_crawler import CompanyList
        root = self._make_one('foo')
        self.assertIsInstance(root.get('companies'), CompanyList)


class CompanyTests(unittest.TestCase):

    def _make_one(self, local_data, name):
        from midas.crunchbase_crawler import Company
        return Company(local_data, name)

    def test_url_generation(self):
        company = self._make_one('foo', 'foo')
        self.assertEqual(company.query_url(), FOO_URL)

    def _make_update(self):
        from midas.crunchbase_crawler import ZippedJsonFile
        with tempfile.NamedTemporaryFile() as fp:
            local_data = ZippedJsonFile(fp.name)
            company = self._make_one(local_data, 'foo')
            company.update()
        return local_data, company

    def test_str(self):
        c = self._make_one(None, 'foo')
        self.assertEqual(str(c), 'Company( foo )')

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_update(self, urlopen):
        prepare_url_open(urlopen,
                         {FOO_URL: {'foo': 'bar', }})
        local_data, company = self._make_update()
        self.assertEqual(local_data.data, {'foo': 'bar'})
        self.assertEqual(company.data, {'foo': 'bar'})
        urlopen.assert_called_once_with(FOO_URL)

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_control_chars_in_response(self, urlopen):
        buf = BytesIO(b'["\x12fo\x14", "ba\x0b"]')
        buf.seek(0)
        urlopen.return_value = buf
        local_data, _ = self._make_update()
        self.assertEqual(local_data.data, ['fo', 'ba'])


class CompanyListTests(unittest.TestCase):

    def _make_one(self, path):
        from midas.crunchbase_crawler import CompanyList
        return CompanyList(DummyRoot(), path)

    def test_local_list_when_company_files_empty(self):
        cl = self._make_one(EXAMPLES_PATH['company_files_empty'])
        result = list(map(str, cl.list_local()))
        result.sort()
        expected = [ 'Company( {0} )'.format(s)
                     for s in ('de-revolutione', 'group-laurier',
                               'hiconversion', 'pivotshare', 'vaporstream') ]
        self.assertEqual(result, expected)

    def test_get(self):
        cl = self._make_one(EXAMPLES_PATH['company_files_empty'])
        result = cl.get('de-revolutione')
        from midas.crunchbase_crawler import Company
        self.assertIsInstance(result, Company)
        self.assertEqual(str(result), 'Company( de-revolutione )')

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_update(self, urlopen):
        prepare_url_open(urlopen,
                         {COMPANIES_URL: [{'permalink': 'foo'}]})
        cl = self._make_one(None)
        cl.update()
        urlopen.assert_called_once_with(COMPANIES_URL)


class ZippedJsonFileTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_one(self, path):
        from midas.crunchbase_crawler import ZippedJsonFile
        return ZippedJsonFile(path)

    def test_dump_and_load(self):
        data = {'foo': ['bar', 'baz']}
        dump_file = os.path.join(self.tmpd, 'dump.json.gz')
        zjf = self._make_one(dump_file)
        zjf.dump(data)
        del zjf
        zjf = self._make_one(dump_file)
        zjf.load()
        self.assertEqual(zjf.data, data)


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_company_fetcher_and_company_list(self, urlopen):
        from midas.crunchbase_crawler import Fetcher
        from midas.crunchbase_crawler import CompanyList
        prepare_url_open(urlopen, {FOO_URL: {'foo': 'bar'}, })
        dump_file = os.path.join(self.tmpd, 'foo.json.gz')
        cl = CompanyList(DummyRoot(), self.tmpd)
        cf = Fetcher(cl.get('foo'),
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(FOO_URL)
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.loads(fp.read().decode()), {'foo': 'bar'})

    def test_crawler_and_company_fetcher_play_together(self):
        from midas.crunchbase_crawler import Updater
        cl = DummyCompanyList()
        cl.list_not_local.return_value = (cl.get('facebook'), )
        crawler = Updater(cl)
        crawler.run()
        fb = cl.get.assert_called_once_with('facebook')
        fb = cl.get('facebook')
        fb.update.assert_called_once_with()
