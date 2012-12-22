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
from midas.compat import StringIO
from midas.compat import unittest

from midas.tests import COMPANIES_URL
from midas.tests import EXAMPLES_PATH
from midas.tests import FOO_URL
from midas.tests import DummyCompany
from midas.tests import DummyCompanyList
from midas.tests import prepare_url_open


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
        return CompanyList(path)

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
