# -*- coding: utf-8 -*-

from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase

class TestGeneratePositiveSamples(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.generate_samples import GeneratePositiveSamples
        return GeneratePositiveSamples

    def test_on_test_data(self):
        self.assertEqual(self._call_cmd(TEST_DATA_PATH['restrictions']), 0)
        self.assert_stdout_equal('foo.example.com\t2012-09-03\n')

