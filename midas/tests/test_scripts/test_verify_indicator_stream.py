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


class TestToString(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.verify_indicator_stream import to_string
        return to_string

    def test_on_simple_example(self):
        example = (1, [(1292024241, bitarray.bitarray('111'))])
        func = self._get_target()
        self.assertEqual(func(*example), 
                         '1\t{(1292024241,(True,True,True))}')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
