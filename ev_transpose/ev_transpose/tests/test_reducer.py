# -*- coding: utf-8 -*-

from datetime import datetime
import sys

from ev_transpose.tests import IntegrationTestCase
from ev_transpose.tests import unittest
from ev_transpose import Entry

import mock

class HelperTests(unittest.TestCase):

    def test_split_name_date_rank(self):
        from ev_transpose.reducer import line_to_entry
        result = line_to_entry('foo\t2012-09-05, 1')
        expected = Entry('foo', datetime(2012, 9, 5), 1)
        self.assertEqual(result, expected)


class ScriptTests(IntegrationTestCase):

    def test_reducer(self):
        from ev_transpose.reducer import reducer
        data = ['foo\t2012-09-05, 1',
                'foo\t2012-09-06, 3',
                'foo\t2012-09-03, 1',
                'foo\t2012-09-04, 2']
        sys.stdin.write('\n'.join(data))
        sys.stdin.seek(0)
        self.assertEqual(reducer(), 0)
        sys.stdout.seek(0)
        out = sys.stdout.getvalue().strip()
        data.sort()
        expected = '\n'.join(data)
        self.assertEqual(out, expected)

    @mock.patch.dict('os.environ', {'TP_MIN_DATE': '2012-09-03'})
    def test_reducer_with_defined_min_date(self):
        from ev_transpose.reducer import reducer
        data = ['foo\t2012-09-05, 1',
                'foo\t2012-09-06, 3',
                'foo\t2012-09-03, 1',
                'foo\t2012-09-04, 2']
        sys.stdin.write('\n'.join(data))
        sys.stdin.seek(0)
        self.assertEqual(reducer(), 0)
        sys.stdout.seek(0)
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), len(data))
        data.sort()
        self.assertEqual(result, data)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
