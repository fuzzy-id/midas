# -*- coding: utf-8 -*-

import bitarray

from midas.compat import unittest
from midas.compat import StringIO

from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase

class TestIterFeatures(unittest.TestCase):

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


class FunctionalTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.verify_indicator_stream import VerifyIndicatorStream
        return VerifyIndicatorStream

    def test_on_test_data(self):
        self.assertEqual(self._call_cmd("3", TEST_DATA_PATH['indicators']), 0)
        self.assert_stdout_equal('1\t{(1292024241,(True,True,True))}\n')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
