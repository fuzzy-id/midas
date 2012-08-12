# -*- coding: utf-8 -*-

import json
import os.path
import shutil
import tempfile

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import DestinationPaths
from crawlcrunch.tests import unittest

import mock

class LocalFilesDirTests(unittest.TestCase):

    def _make_one(self, path):
        from crawlcrunch.model import LocalFilesDir
        return LocalFilesDir(path)

    def test_companies_list_creation(self):
        root = self._make_one('foo')
        companies = root.get('companies')
        from crawlcrunch.model import CompanyList
        self.assertIsInstance(companies, CompanyList)

    def test_nodes_are_not_created_twice(self):
        root = self._make_one('foo')
        self.assertIs(root.get('companies'), root.get('companies'))

class CompanyTests(unittest.TestCase):

    def _make_one(self, path, name):
        from crawlcrunch.model import LocalFilesDir
        root = LocalFilesDir(path)
        return root.get(name)

    def test_url_generation(self):
        company = self._make_one('foo', 'facebook')
        expected = 'http://api.crunchbase.com/v/1/company/facebook.js'
        self.assertEqual(company.query_url(), expected)

class CompanyListTests(unittest.TestCase):

    def _make_one(self, path):
        from crawlcrunch.model import LocalFilesDir
        root = LocalFilesDir(path)
        return root.get('companies')

    def test_list_creation_when_all_companies_files_present(self):
        cl = self._make_one(DestinationPaths.companies_empty)
        cl.load()
        self.assertEqual(list(cl.not_local()), [])

    def test_list_creation_when_companies_missing(self):
        cl = self._make_one(DestinationPaths.no_companies)
        cl.load()
        cl.sort()
        self.assertEqual(cl, [ 'de-revolutione',
                               'group-laurier',
                               'hiconversion',
                               'pivotshare',
                               'vaporstream',
                               ])

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_one(self, path):
        from crawlcrunch.model import LocalFilesDir
        return LocalFilesDir(path)

    def _make_json_buffer(self, content):
        json_buffer = StringIO()
        json.dump(content, json_buffer)
        json_buffer.seek(0)
        return json_buffer

    @mock.patch('crawlcrunch.model.url_open')
    def test_list_is_fetched_and_saved_when_not_present(self, 
                                                        url_open):
        url_open.return_value = self._make_json_buffer(
            [{'permalink': 'foo'}, ])
        from crawlcrunch.model import CompaniesList
        root = self._make_one(self.tmpd)
        companies = root.get('companies')
        companies.update()
        url_open.assert_called_once_with(
            'http://api.crunchbase.com/v/1/companies.js')
        companies_file = (os.path.join(self.tmpd, 
                                       'companies.json.gz'))
        self.assertTrue(os.path.isfile(companies_file))
        with GzipFile(companies_file) as fp:
            self.assertEqual(json.load(fp), 
                             [{'permalink': 'foo'}, ])
