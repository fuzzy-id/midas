# -*- coding: utf-8 -*-

from StringIO import StringIO
import json
import os.path
import shutil
import tempfile

import mock

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import unittest
from crawlcrunch.tests import DestinationPaths

class CompaniesListTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.companies import CompaniesList
        return CompaniesList

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_list_creation_when_all_companies_files_present(self):
        cl = self._make_one(DestinationPaths.companies_empty)
        cl.create_list()
        self.assertEqual(cl.companies, [])

    def test_list_creation_when_companies_missing(self):
        cl = self._make_one(DestinationPaths.no_companies)
        cl.create_list()
        cl.companies.sort()
        self.assertEqual(cl.companies, [ 'de-revolutione',
                                         'group-laurier',
                                         'hiconversion',
                                         'pivotshare',
                                         'vaporstream',
                                         ])

    def test_companies_list_is_iterable(self):
        cl = self._make_one('foo')
        cl.companies = ['foo', 'bar']
        result = list(cl)
        self.assertEqual(result, ['foo', 'bar'])

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_json_buffer(self, content):
        json_buffer = StringIO()
        json.dump(content, json_buffer)
        json_buffer.seek(0)
        return json_buffer


    @mock.patch('urllib2.urlopen')
    def test_list_is_fetched_and_saved_when_not_present(self, 
                                                        urlopen):
        urlopen.return_value = self._make_json_buffer(
            [{'permalink': 'foo'}, ])
        from crawlcrunch.companies import CompaniesList
        cl = CompaniesList(self.tmpd)
        cl.create_list()
        urlopen.assert_called_once_with(
            'http://api.crunchbase.com/v/1/companies.js')
        companies_file = (os.path.join(self.tmpd, 
                                       'companies.json.gz'))
        self.assertTrue(os.path.isfile(companies_file))
        with GzipFile(companies_file) as fp:
            self.assertEqual(json.load(fp), [{'permalink': 'foo'}, ])
