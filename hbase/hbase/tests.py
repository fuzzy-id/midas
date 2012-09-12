# -*- coding: utf-8 -*-

from hbase.compat import PY26

import mock

if PY26:
    import unittest2 as unittest
else:
    import unittest


class TableListTests(unittest.TestCase):

    def _make_one(self):
        from hbase import HBase
        return HBase('localhost', '8080')

    @mock.patch("hbase.compat.urlopen")
    def test_query_tables_list(self, urlopen):
        urlopen().readall.return_value = b'{"table":[{"name":"test"}]}'
        hb_con = self._make_one()
        self.assertEqual(list(hb_con.get_tables()), ['test'])

    @mock.patch("hbase.compat.urlopen")
    def test_query_version_information(self, urlopen):
        urlopen().readall.return_value = b'{"JVM":"Oracle Corporation 1.7.0_07-23.3-b01","Jersey":"1.8","OS":"Linux 3.4.2-x86_64-linode25 amd64","REST":"0.0.2","Server":"jetty/6.1.26"}'
        hb_con = self._make_one()
        self.assertEqual(hb_con.get_version(), {"JVM": "Oracle Corporation 1.7.0_07-23.3-b01",
                                                "Jersey": "1.8",
                                                "OS": "Linux 3.4.2-x86_64-linode25 amd64",
                                                "REST": "0.0.2",
                                                "Server": "jetty/6.1.26"})
