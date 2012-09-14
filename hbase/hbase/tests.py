# -*- coding: utf-8 -*-

from hbase.compat import PY26
from hbase.compat import comp_bytes

import mock

if PY26:  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest


class HelperTests(unittest.TestCase):

    def test_str64decode(self):
        from hbase import str64decode
        result = str64decode('YmFy')
        self.assertEqual(result, 'bar')

    def test_str64encode(self):
        from hbase import str64encode
        result = str64encode('bar')
        self.assertEqual(result, 'YmFy')


class MakeRequestTests(unittest.TestCase):

    def _get_target_func(self):
        from hbase import HBBase
        class Wrapper(HBBase):
            _base_url = 'http://example.com/'
        return Wrapper()._make_request

    def test_call_without_args(self):
        func = self._get_target_func()
        req = func()
        self.assertEqual(req.get_full_url(), 'http://example.com/')

    def test_path_expansion(self):
        func = self._get_target_func()
        req = func('foo', 'bar')
        self.assertEqual(req.get_full_url(), 'http://example.com/foo/bar')

    def test_w_str_as_data(self):
        func = self._get_target_func()
        req = func('foo', data='bar')
        self.assertEqual(req.data, b'bar')
        self.assertEqual(req.headers['Content-type'],
                         'application/octet-stream')
    
    def test_w_list_as_data(self):
        func = self._get_target_func()
        req = func('foo', data=['bar'])
        self.assertEqual(req.data, b'["bar"]')
        self.assertEqual(req.headers['Content-type'],
                         'application/json')
    

class TableListTests(unittest.TestCase):

    def _make_one(self):
        from hbase import HBConnection
        return HBConnection('localhost', '8080')

    @mock.patch("hbase.compat.urlopen")
    def test_query_tables_list(self, urlopen):
        urlopen().readall.return_value = b'{"table":[{"name":"test"}]}'
        hb_con = self._make_one()
        self.assertEqual(hb_con.tables, ['test'])

    @mock.patch("hbase.compat.urlopen")
    def test_query_version_information(self, urlopen):
        urlopen().readall.return_value = comp_bytes(
            ','.join(['{"JVM":"Oracle Corporation 1.7.0_07-23.3-b01"',
                      '"Jersey":"1.8"',
                      '"OS":"Linux 3.4.2-x86_64-linode25 amd64"',
                      '"REST":"0.0.2","Server":"jetty/6.1.26"}']), 'utf-8')
        hb_con = self._make_one()
        self.assertEqual(hb_con.version, 
                         {"JVM": "Oracle Corporation 1.7.0_07-23.3-b01",
                          "Jersey": "1.8",
                          "OS": "Linux 3.4.2-x86_64-linode25 amd64",
                          "REST": "0.0.2",
                          "Server": "jetty/6.1.26"})
