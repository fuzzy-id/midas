# -*- coding: utf-8 -*-

from io import BytesIO
import json
import tempfile

import mock

from midas.compat import GzipFile
from midas.compat import unittest
from midas.tests import COMPANIES_URL
from midas.tests import TEST_DATA_PATH
from midas.tests import FOO_URL
from midas.tests import prepare_url_open


class CompanyTests(unittest.TestCase):

    def _make_one(self, name, fname):
        from midas.crunchbase_company import Company
        return Company(name, fname)

    def _make_update(self):
        from midas.crunchbase_company import Company
        with tempfile.NamedTemporaryFile() as fp:
            company = self._make_one('foo', fp.name)
            company.update()
        return company

    def test_url_generation(self):
        company = self._make_one('foo', None)
        self.assertEqual(company.query_url(), FOO_URL)

    def test_str(self):
        c = self._make_one('foo', None)
        self.assertEqual(str(c), 'Company( foo )')

    @mock.patch('midas.crunchbase_company.urlopen')
    def test_update(self, urlopen):
        prepare_url_open(urlopen, {FOO_URL: {'foo': 'bar', }})
        company = self._make_update()
        self.assertEqual(company.data, {'foo': 'bar'})
        urlopen.assert_called_once_with(FOO_URL)

    @mock.patch('midas.crunchbase_company.urlopen')
    def test_control_chars_in_response(self, urlopen):
        buf = BytesIO(b'["\x12fo\x14", "ba\x0b"]')
        buf.seek(0)
        urlopen.return_value = buf
        company = self._make_update()
        self.assertEqual(company.data, ['fo', 'ba'])

    def test_loading_data_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w+') as tmpf:
            tmpf.write(json.dumps({'foo': 'bar'}))
            tmpf.seek(0)
            c = self._make_one('TestCompany', tmpf.name)
            c.load()
        self.assertEqual(c.data, {'foo': 'bar'})


class CompanyListTests(unittest.TestCase):

    def _make_one(self, path):
        from midas.crunchbase_company import CompanyList
        return CompanyList(path)

    def test_local_list_when_company_files_empty(self):
        cl = self._make_one(TEST_DATA_PATH['crunchbase_companies'])
        result = list(map(str, cl.list_local()))
        result.sort()
        expected = [ 'Company( {0} )'.format(s)
                     for s in ('baz-bar', 'foo') ]
        self.assertEqual(result, expected)

    def test_get(self):
        cl = self._make_one('non/existent/path')
        result = cl.get('foo')
        from midas.crunchbase_company import Company
        self.assertIsInstance(result, Company)
        self.assertEqual(str(result), 'Company( foo )')

    @mock.patch('midas.crunchbase_company.urlopen')
    def test_update(self, urlopen):
        prepare_url_open(urlopen, {COMPANIES_URL: [{'permalink': 'foo'}]})
        cl = self._make_one(None)
        cl.update()
        urlopen.assert_called_once_with(COMPANIES_URL)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
