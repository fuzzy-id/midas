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

    def test_parse_line(self):
        from ev_transpose.mapper import split_rank_name
        result = split_rank_name('1,foo')
        self.assertEqual(result, (1, 'foo'))

    def test_parse_line_w_comma_in_name(self):
        ' This seems to happen. *sigh* '
        from ev_transpose.mapper import split_rank_name
        result = split_rank_name('1,foo,bar')
        self.assertEqual(result, (1, 'foo,bar'))

    def test_normalize_name(self):
        from ev_transpose.mapper import normalize_site
        self.assertEqual('example.com', normalize_site('example.com'))
        self.assertEqual('example.com', normalize_site('http://www.example.com/'))
        self.assertEqual('example.com', normalize_site('www.example.com/foo'))
