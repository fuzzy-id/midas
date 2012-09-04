# -*- coding: utf-8 -*-

from io import BytesIO

import json
import os.path
import shutil
import tempfile

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import EXAMPLES_PATH
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest

import mock


class LocalFilesRootTests(unittest.TestCase):

    def _make_one(self, path):
        from crawlcrunch.model.local_files import LocalFilesRoot
        return LocalFilesRoot(path)

    def test_companies_list_creation(self):
        root = self._make_one('foo')
        companies = root.get('companies')
        from crawlcrunch.model.local_files import CompanyList
        self.assertIsInstance(companies, CompanyList)


class CompanyTests(unittest.TestCase):

    def _make_one(self, path, name):
        from crawlcrunch.model.local_files import LocalFilesRoot
        root = LocalFilesRoot(path)
        return root.get(name)

    def test_url_generation(self):
        company = self._make_one('foo', 'facebook')
        expected = 'http://api.crunchbase.com/v/1/company/facebook.js'
        self.assertEqual(company.query_url(), expected)

    @mock.patch('crawlcrunch.model.local_files.url_open')
    def test_update(self, url_open):
        foo_url = 'http://api.crunchbase.com/v/1/company/foo.js'
        prepare_url_open(url_open,
                         {foo_url: {'foo': 'bar', }})
        from crawlcrunch.model.local_files import ZippedJsonFile
        from crawlcrunch.model.local_files import Company
        with tempfile.NamedTemporaryFile() as fp:
            local_data = ZippedJsonFile(fp.name)
            company = Company(local_data, 'foo')
            company.update()
        self.assertEqual(local_data.data, {'foo': 'bar'})
        self.assertEqual(company.data, {'foo': 'bar'})
        url_open.assert_called_once_with(foo_url)

    @mock.patch('crawlcrunch.model.local_files.url_open')
    def test_control_chars_in_response(self, urlopen):
        buf = BytesIO(b'["\x12fo\x14", "ba\x0b"]')
        buf.seek(0)
        urlopen.return_value = buf
        from crawlcrunch.model.local_files import ZippedJsonFile
        from crawlcrunch.model.local_files import Company
        with tempfile.NamedTemporaryFile() as fp:
            local_data = ZippedJsonFile(fp.name)
            company = Company(local_data, 'foo')
            company.update()
        self.assertEqual(local_data.data, ['fo', 'ba'])


class CompanyListTests(unittest.TestCase):

    def _make_one(self, path):
        from crawlcrunch.model.local_files import LocalFilesRoot
        root = LocalFilesRoot(path)
        return root.get('companies')

    def test_list_creation_when_all_companies_files_present(self):
        cl = self._make_one(EXAMPLES_PATH['company_files_empty'])
        cl.load()
        self.assertEqual(list(cl.not_local()), [])

    def test_list_creation_when_companies_missing(self):
        cl = self._make_one(EXAMPLES_PATH['no_company_files'])
        cl.load()
        cl.sort()
        expected = ['de-revolutione', 'group-laurier',
                    'hiconversion', 'pivotshare', 'vaporstream']
        self.assertEqual(cl, expected)

    def test_local_list_when_companies_missing(self):
        cl = self._make_one(EXAMPLES_PATH['company_files_empty'])
        cl.load()
        cl.sort()
        expected = ['de-revolutione', 'group-laurier',
                    'hiconversion', 'pivotshare', 'vaporstream']
        self.assertEqual(list(cl.list_local()), expected)

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_one(self, path):
        from crawlcrunch.model.local_files import LocalFilesRoot
        return LocalFilesRoot(path)

    @unittest.skip('rebuilding things')
    @mock.patch('crawlcrunch.model.local_files.url_open')
    def test_list_is_fetched_when_not_present(self, url_open):
        url = 'http://api.crunchbase.com/v/1/companies.js'
        prepare_url_open(url_open,
                         {url: [{'permalink': 'foo'}]})
        from crawlcrunch.model.local_files import CompanyList
        root = self._make_one(self.tmpd)
        companies = root.get('companies')
        companies.update()
        url_open.assert_called_once_with(url)
        companies_file = (os.path.join(self.tmpd,
                                       'companies.json.gz'))
        self.assertTrue(os.path.isfile(companies_file))
        with GzipFile(companies_file) as fp:
            self.assertEqual(json.load(fp),
                             [{'permalink': 'foo'}, ])
