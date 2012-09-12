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
