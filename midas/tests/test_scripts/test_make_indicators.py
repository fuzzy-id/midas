# -*- coding: utf-8 -*-

import io
import os.path

import bitarray
import mock
import yaml

from midas.compat import unittest
from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import IntegrationTestCase
from midas.tests.test_scripts import MDCommandTestCase

CONF = {'exec': 'non_existent',
        'rsi': {'ndays': {'start': 0,
                          'stop': 3,
                          'step': 2},
                'thresholds': {'start': 0,
                               'stop': 2}}}


class TestIterFeatures(unittest.TestCase):

    def get_target(self):
        from midas.scripts.make_indicators import iter_features
        return iter_features

    def test_simple_example(self):
        buf = BytesIO(b'\x01\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00')
        func = self.get_target()
        result = list(func(buf, 3))
        expected = [(1, [(1292024241, bitarray.bitarray('111'))])]
        self.assertEqual(result, expected)


class TestToString(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_indicators import to_string
        return to_string

    def test_on_simple_example(self):
        example = (1, [(1292024241, bitarray.bitarray('111'))])
        func = self._get_target()
        self.assertEqual(func(*example), 
                         '1\t{(1292024241,(True,True,True))}')


class FunctionalTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.make_indicators import VerifyIndicatorStream
        return VerifyIndicatorStream

    def test_on_test_data(self):
        self.assertEqual(self._call_cmd("3", TEST_DATA_PATH['indicators']), 0)
        self.assert_stdout_equal('1\t{(1292024241,(True,True,True))}\n')


class ExpandConfigTests(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_indicators import expand_config
        return expand_config

    def test_start_stop_step_on_ndays_and_threshold(self):
        func = self._get_target()
        result = func(CONF)
        expected = [('rsi', 0, 0), ('rsi', 0, 1), ('rsi', 2, 0), ('rsi', 2, 1)]
        self.assertEqual(list(result), expected)

    def test_list_on_ndays_and_threshold(self):
        func = self._get_target()
        result = func({'rsi': {'ndays': [0, 1],
                               'thresholds': [0, 2]}})
        expected = [('rsi', 0, 0), ('rsi', 0, 2), ('rsi', 1, 0), ('rsi', 1, 2)]
        self.assertEqual(list(result), expected)

    def test_pearson_list_on_ndays_and_threshold(self):
        func = self._get_target()
        result = func({'pearson': {'ndays': {'start': 0,
                                             'stop': 1},
                                   'thresholds': {'start': 0,
                                                  'stop': 3,
                                                  'step': 2}}})
        expected = [('pearson', 0, 0), ('pearson', 0, 2)]
        self.assertEqual(list(result), expected)


class GenerateNamesTests(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_indicators import generate_names
        return generate_names

    def test_some(self):
        func = self._get_target()
        result = func(CONF)
        expected = """
class.

site:\tlabel.
class:\tseed, angel, a, negative.
rsi_0_0:\tTrue, False.
rsi_0_1:\tTrue, False.
rsi_2_0:\tTrue, False.
rsi_2_1:\tTrue, False.
"""
        self.assertEqual(result, expected)


class CallStreamAlexaIndicatorsTests(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_indicators import call_stream_alexa_indicators
        return call_stream_alexa_indicators

    @mock.patch("subprocess.Popen")
    def test_mocked_popen(self, Popen):
        Popen().stdout = io.BytesIO(b'\x01\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00')
        Popen().poll.return_value = 0
        func = self._get_target()
        result = list(func(CONF))
        expected = [(1, [(1292024241, bitarray.bitarray('1110'))])]
        self.assertEqual(result, expected)


class IntegrationTests(IntegrationTestCase):

    def _get_target_cls(self):
        from midas.scripts.make_indicators import MakeAlexaIndicators
        return MakeAlexaIndicators

    @mock.patch("subprocess.Popen")
    def test_mocked_popen(self, Popen):
        Popen().stdout = io.BytesIO(b'\x01\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00')
        Popen().poll.return_value = 0
        names_f = os.path.join(self.tmpd, 'indicators.names')
        indicators_f = os.path.join(self.tmpd, 'indicators')
        conf_f = os.path.join(self.tmpd, 'conf.yml')
        with open(conf_f, 'w') as fp:
            fp.write(yaml.safe_dump(CONF))
        self.assertEqual(self._call_cmd(names_f, indicators_f, conf_f), 0)
        with open(indicators_f) as fp:
            self.assertEqual(fp.read(), '1\t{(1292024241,(True,True,True,False))}\n')
        with open(names_f) as fp:
            self.assertTrue(fp.read().startswith('\nclass'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
