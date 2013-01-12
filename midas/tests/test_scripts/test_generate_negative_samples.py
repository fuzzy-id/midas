# -*- coding: utf-8 -*-

from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase

class Tests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.generate_negative_samples import GenerateNegativeSamples
        return GenerateNegativeSamples

    def test_on_test_data(self):
        self.assertEqual(self._call_cmd(TEST_DATA_PATH['restrictions']), 0)
        self.assert_stdout_equal('foo.example.com\t2012-09-03\n')

