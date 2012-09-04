# -*- coding: utf-8 -*-

from io import BytesIO

import json
import os.path
import shutil
import tempfile

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import EXAMPLES_PATH
from crawlcrunch.tests import DummyRoot
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest

import mock


class LocalFilesRootTests(unittest.TestCase):

    def _make_one(self, path):
        from crawlcrunch.model.local_files import LocalFilesRoot
        return LocalFilesRoot(path)

    def test_companies_list_creation(self):
        from crawlcrunch.model.local_files import CompanyList
        root = self._make_one('foo')
        self.assertIsInstance(root.get('companies'), CompanyList)


class CompanyTests(unittest.TestCase):

    def _make_one(self, local_data, name):
        from crawlcrunch.model.local_files import Company
        return Company(local_data, name)

    def test_url_generation(self):
        company = self._make_one('foo', 'facebook')
        expected = 'http://api.crunchbase.com/v/1/company/facebook.js'
        self.assertEqual(company.query_url(), expected)

    def _make_update(self):
        from crawlcrunch.model.local_files import ZippedJsonFile
        with tempfile.NamedTemporaryFile() as fp:
            local_data = ZippedJsonFile(fp.name)
            company = self._make_one(local_data, 'foo')
            company.update()
        return local_data, company

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_update(self, urlopen):
        foo_url = 'http://api.crunchbase.com/v/1/company/foo.js'
        prepare_url_open(urlopen,
                         {foo_url: {'foo': 'bar', }})
        local_data, company = self._make_update()
        self.assertEqual(local_data.data, {'foo': 'bar'})
        self.assertEqual(company.data, {'foo': 'bar'})
        urlopen.assert_called_once_with(foo_url)

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_control_chars_in_response(self, urlopen):
        buf = BytesIO(b'["\x12fo\x14", "ba\x0b"]')
        buf.seek(0)
        urlopen.return_value = buf
        local_data, _ = self._make_update()
        self.assertEqual(local_data.data, ['fo', 'ba'])


class CompanyListTests(unittest.TestCase):

    def _make_one(self, path):
        from crawlcrunch.model.local_files import CompanyList
        return CompanyList(DummyRoot(), path)

    def test_local_list_when_company_files_empty(self):
        cl = self._make_one(EXAMPLES_PATH['company_files_empty'])
        result = list(cl.list_local())
        result.sort()
        expected = ['de-revolutione', 'group-laurier',
                    'hiconversion', 'pivotshare', 'vaporstream']
        self.assertEqual(result, expected)

    def test_get(self):
        cl = self._make_one(EXAMPLES_PATH['company_files_empty'])
        result = cl.get('de-revolutione')
        from crawlcrunch.model.local_files import Company
        self.assertIsInstance(result, Company)
        self.assertEqual(result.name, 'de-revolutione')


class IntegrationTests(unittest.TestCase):

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_list_is_fetched_when_not_present(self, urlopen):
        url = 'http://api.crunchbase.com/v/1/companies.js'
        prepare_url_open(urlopen,
                         {url: [{'permalink': 'foo'}]})
        from crawlcrunch.model.local_files import CompanyList
        companies = CompanyList(DummyRoot(), None)
        companies.update()
        urlopen.assert_called_once_with(url)
