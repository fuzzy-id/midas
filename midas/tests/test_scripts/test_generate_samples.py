# -*- coding: utf-8 -*-

from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase


class TestGenerateNegativeSamples(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.generate_samples import GenerateNegativeSamples
        return GenerateNegativeSamples

    def test_on_constructed_data(self):
        self.stdin.write('\n'.join(['foo.example.com\t{(2012-09-02,1)}',
                                    'bar.example.com\t{(2012-09-02,3)}',
                                    '']))
        self.assertEqual(self._call_cmd(TEST_DATA_PATH['restrictions']), 0)
        self.assert_stdout_equal('foo.example.com\t2012-09-03\tnegative\n')


class TestGeneratePositiveSamples(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.generate_samples import GeneratePositiveSamples
        return GeneratePositiveSamples

    def test_on_test_data(self):
        self.assertEqual(self._call_cmd(TEST_DATA_PATH['restrictions']), 0)
        self.assert_stdout_equal('foo.example.com\t2012-09-03\tseed\n')
