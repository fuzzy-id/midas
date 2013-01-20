# -*- coding: utf-8 -*-

import bitarray

from midas.compat import unittest
from midas.compat import StringIO

class Tests(unittest.TestCase):

    def get_target(self):
        from midas.scripts.verify_indicator_stream import iter_features
        return iter_features

    def test_simple_example(self):
        buf = StringIO(b'\x01\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00')
        func = self.get_target()
        result = list(func(buf, 3))
        expected = [(1, [(1292024241, bitarray.bitarray('111'))])]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
