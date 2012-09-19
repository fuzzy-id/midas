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
        foos = ['foo\t2012-09-05, 1',
                'foo\t2012-09-06, 3',
                'foo\t2012-09-03, 1',
                'foo\t2012-09-04, 2']
        bars = ['bar\t2012-09-05, 1',
                'bar\t2012-09-06, 3',
                'bar\t2012-09-03, 1',
                'bar\t2012-09-04, 2']
        sys.stdin.write('\n'.join(foos + bars))
        sys.stdin.seek(0)
        self.assertEqual(reducer(), 0)
        sys.stdout.seek(0)
        out = sys.stdout.getvalue().strip()
        foos.sort()
        bars.sort()
        expected = '\n'.join(foos + bars)
        self.assertEqual(out, expected)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
