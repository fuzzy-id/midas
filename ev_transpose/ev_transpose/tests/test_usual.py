# -*- coding: utf-8 -*-

from ev_transpose.tests import TEST_DATA
from ev_transpose.tests import unittest


class SomeTests(unittest.TestCase):

    def test_unzipping_file(self):
        from ev_transpose import unzip_file
        result = list(unzip_file(TEST_DATA[0][0]))
        expected = [ '{e.rank},{e.name}'.format(e=entry)
                     for entry in TEST_DATA[0][1] ]
        self.assertEqual(result, expected)
