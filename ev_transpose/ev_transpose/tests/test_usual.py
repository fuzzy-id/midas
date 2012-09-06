# -*- coding: utf-8 -*-

import sys

from ev_transpose.compat import StringIO
from ev_transpose.tests import TEST_DATA
from ev_transpose.tests import unittest


class SomeTests(unittest.TestCase):

    def test_unzipping_file(self):
        from ev_transpose import unzip_file
        result = list(unzip_file(TEST_DATA[0][0]))
        expected = [ '{e.rank},{e.name}'.format(e=entry)
                     for entry in TEST_DATA[0][1] ]
        self.assertEqual(result, expected)

    def test_parse_line(self):
        from ev_transpose import split_rank_name
        result = split_rank_name('1,foo')
        self.assertEqual(result, (1, 'foo'))


class ScriptTests(unittest.TestCase):

    def setUp(self):
        self._oldout = sys.stdout
        sys.stdout = StringIO()
        self._oldin = sys.stdin
        sys.stdin = StringIO()

    def tearDown(self):
        sys.stdout = self._oldout
        sys.stdin = self._oldin
    
    def test_mapper(self):
        from ev_transpose.scripts import mapper
        sys.stdin.write(TEST_DATA[0][0])
        sys.stdin.seek(0)
        self.assertEqual(mapper(), 0)
        sys.stdout.seek(0)
        out = sys.stdout.getvalue()
        expected = '\n'.join('{e.name}\t{e.date},{e.rank}'.format(e=entry)
                             for entry in TEST_DATA[0][1])
        self.assertEqual(out.strip(), expected)

    @unittest.skip
    def test_reducer(self):
        from ev_transpose.scripts import reducer
        data = ['foo\t2012-09-05,1',
                'foo\t2012-09-03,1',
                'foo\t2012-09-06,3',
                'foo\t2012-09-04,2']
        sys.stdin.write('\n'.join(data))
        self.assertEqual(reducer(), 0)
        sys.stdout.seek(0)
        out = sys.stdout.getvalue()
        data.sort()
        expected = '\n'.join(data)
        self.assertEqual(out, expected)
