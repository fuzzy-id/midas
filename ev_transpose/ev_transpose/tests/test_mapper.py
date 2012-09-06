# -*- coding: utf-8 -*-

import sys

from ev_transpose.tests import TEST_DATA
from ev_transpose.tests import IntegrationTestCase
from ev_transpose.tests import unittest


class HelperTests(unittest.TestCase):

    def test_unzipping_file(self):
        from ev_transpose.mapper import unzip_file
        result = list(unzip_file(TEST_DATA[0][0]))
        expected = [ '{e.rank},{e.name}'.format(e=entry)
                     for entry in TEST_DATA[0][1] ]
        self.assertEqual(result, expected)

    def test_unzipping_file_w_trailing_newline(self):
        from ev_transpose.mapper import unzip_file
        result = list(unzip_file(TEST_DATA[0][0] + '\n'))
        expected = [ '{e.rank},{e.name}'.format(e=entry)
                     for entry in TEST_DATA[0][1] ]
        self.assertEqual(result, expected)

    def test_parse_line(self):
        from ev_transpose.mapper import split_rank_name
        result = split_rank_name('1,foo')
        self.assertEqual(result, (1, 'foo'))

    def test_convert_fname_to_tstamp_w_trailing_newline(self):
        from ev_transpose.mapper import convert_fname_to_tstamp
        result = convert_fname_to_tstamp('~/top-1m-2012-03-03.csv.zip\n')
        self.assertEqual(result, '2012-03-03')


class ScriptTests(IntegrationTestCase):

    def test_mapper(self):
        from ev_transpose.mapper import mapper
        sys.stdin.write(TEST_DATA[0][0])
        sys.stdin.seek(0)
        self.assertEqual(mapper(), 0)
        sys.stdout.seek(0)
        out = sys.stdout.getvalue()
        expected = '\n'.join('{e.name}\t{e.date}, {e.rank}'.format(e=entry)
                             for entry in TEST_DATA[0][1])
        self.assertEqual(out.strip(), expected)
