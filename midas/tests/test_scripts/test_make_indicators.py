# -*- coding: utf-8 -*-

import copy
import datetime
import io
import os.path
import subprocess

import bitarray
import mock
import yaml

from midas.compat import unittest
from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import IntegrationTestCase
from midas.tests.test_scripts import MDCommandTestCase

CONF = {'executable': 'non_existent',
        'num_threads': 1,
        'ids_to_sites': TEST_DATA_PATH['ids_to_sites'],
        'samples': TEST_DATA_PATH['samples'],
        'rsi': {'ndays': {'start': 0,
                          'stop': 3,
                          'step': 2},
                'thresholds': {'start': 0,
                               'stop': 2}}}


class IterFeaturesTests(unittest.TestCase):

    def get_target(self):
        from midas.scripts.make_indicators import iter_features
        return iter_features

    def test_simple_example(self):
        buf = io.BytesIO(
            b'\x01\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00'
            )
        func = self.get_target()
        result = list(func(buf, 3))
        expected = [(1, [(1292024241, bitarray.bitarray('111'))])]
        self.assertEqual(result, expected)

    def test_a_bit_more_advanced_example(self):
        buf = io.BytesIO(
            b'\x01\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00'
            + b'\x02\x00\x00\x00\xb1\xb9\x02M\x07\x00\x00\x00\x00'
            )
        func = self.get_target()
        result = list(func(buf, 3))
        expected = [(1, [(1292024241, bitarray.bitarray('111'))]),
                    (2, [(1292024241, bitarray.bitarray('111'))])]
        self.assertEqual(result, expected)


class ToStringTests(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_indicators import to_string
        return to_string

    def test_on_simple_example(self):
        example = (1, [(1292024241, bitarray.bitarray('111'))])
        func = self._get_target()
        self.assertEqual(func(*example), 
                         '1\t{(1292024241,(True,True,True))}')


class VerifyIndicatorStreamTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.make_indicators import VerifyIndicatorStream
        return VerifyIndicatorStream

    def test_on_test_data(self):
        self.assertEqual(self._call_cmd("3", TEST_DATA_PATH['indicators']), 0)
        self.assert_stdout_equal('1\t{(1292024241,(True,True,True))}\n')


class CallStreamAlexaIndicatorsTests(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_indicators import StreamAlexaIndicatorsCaller
        return StreamAlexaIndicatorsCaller

    @mock.patch("subprocess.Popen")
    def test_mocked_popen(self, Popen):
        Popen().stdout = io.BytesIO(
            b'\x01\x00\x00\x00\xb1\xb9\x02M\x01\x00\x00\x00\x00'
            )
        Popen().wait.return_value = 0
        dummy_indicator = mock.MagicMock()
        dummy_indicator.threshold = 0
        cls = self._get_target()
        obj = cls('non_existent_cmd')
        result = list(obj.call(dummy_indicator))
        expected = [(1, [(1292024241, bitarray.bitarray('1'))])]
        self.assertEqual(result, expected)


class CreateFeaturesTests(IntegrationTestCase):

    def _get_target_cls(self):
        from midas.scripts.make_indicators import CreateFeatures
        return CreateFeatures

    def _make_conf(self, conf=CONF):
        if conf is CONF:
            conf = copy.copy(CONF)
        if 'indicators_cache' not in conf:
            conf['indicators_cache'] = self.tmpd
        conf_f = os.path.join(self.tmpd, 'some.yml')
        with open(conf_f, 'w') as fp:
            fp.write(yaml.dump(conf))
        return conf_f

    def test_names(self):
        cls = self._get_target_cls()
        obj = cls(['cmd', self._make_conf()])
        expected = """class.

site:\tlabel.
class:\tseed, angel, a, negative.
rsi_0_0.00:\tTrue, False.
rsi_0_1.00:\tTrue, False.
rsi_2_0.00:\tTrue, False.
rsi_2_1.00:\tTrue, False.
"""
        self.assertEqual(obj.names, expected)

    def test_indicators_start_stop_step_on_ndays_and_threshold(self):
        cls = self._get_target_cls()
        obj = cls(['cmd', self._make_conf(), ])
        expected = ['rsi_0_0.00', 'rsi_0_1.00', 'rsi_2_0.00', 'rsi_2_1.00']
        self.assertEqual(list(map(str, obj.indicators)), expected)

    def test_rank_feature(self):
        cls = self._get_target_cls()
        conf = copy.copy(CONF)
        del conf['rsi']
        conf['rank'] = {'thresholds': [10, 20]}
        obj = cls(['cmd', self._make_conf(conf)])
        expected = ['rank_10', 'rank_20']
        self.assertEqual(list(map(str, obj.indicators)), expected)

    def test_list_on_ndays_and_threshold(self):
        cls = self._get_target_cls()
        conf = copy.copy(CONF)
        conf['rsi'] = {'ndays': [0, 1],
                       'thresholds': [0, 2]}
        obj = cls(['cmd', self._make_conf(conf)])
        expected = ['rsi_0_0.00', 'rsi_0_2.00', 'rsi_1_0.00', 'rsi_1_2.00']
        self.assertEqual(list(map(str, obj.indicators)), expected)

    def test_sites_to_ids(self):
        cls = self._get_target_cls()
        obj = cls(['cmd', self._make_conf()])
        expected = {'baz.bar.example.com': 1,
                    'foo.example.com': 2}
        self.assertEqual(obj.sites_to_ids, expected)

    def test_ids_to_samples(self):
        cls = self._get_target_cls()
        obj = cls(['cmd', '-q', self._make_conf()])
        expected = {1: ('baz.bar.example.com', 
                        datetime.datetime(2010, 12, 13),
                        'negative'),
                    2: ('foo.example.com', 
                        datetime.datetime(2010, 12, 14),
                        'angel')}
        self.assertEqual(obj.ids_to_samples, expected)

    @mock.patch("subprocess.Popen")
    def test_rsi_with_mocked_popen(self, Popen):
        Popen().stdout = io.BytesIO(
            b'\x01\x00\x00\x00\xb1\xb9\x02M\x01\x00\x00\x00\x00'
            + b'\x02\x00\x00\x00\xb1\xb9\x02M\x01\x00\x00\x00\x00'
            )
        Popen().wait.return_value = 0
        names_f = os.path.join(self.tmpd, 'some.names')
        data_f = os.path.join(self.tmpd, 'some.data')
        conf = copy.copy(CONF)
        conf['rsi'] = {'ndays': [0, ],
                       'thresholds': [0, ]}
        self.assertEqual(self._call_cmd('-y', self._make_conf(conf)), 0)
        Popen.assert_called_with(['non_existent', '--dbpivot', 'rsi,0,0.00'], 
                                 stdout=subprocess.PIPE)
        with open(data_f) as fp:
            expected = ['baz.bar.example.com,negative,True',
                        'foo.example.com,angel,True']
            for result, expect in zip(fp, expected):
                self.assertEqual(result.rstrip(), expect)
        with open(names_f) as fp:
            self.assertTrue(fp.read().startswith('class'))

    @mock.patch("subprocess.Popen")
    def test_rsi_with_mocked_popen(self, Popen):
        Popen().stdout = io.BytesIO(
            b'\x01\x00\x00\x00\xb1\xb9\x02M\x01\x00\x00\x00\x00'
            + b'\x02\x00\x00\x00\xb1\xb9\x02M\x01\x00\x00\x00\x00'
            )
        Popen().wait.return_value = 0
        names_f = os.path.join(self.tmpd, 'some.names')
        data_f = os.path.join(self.tmpd, 'some.data')
        conf = copy.copy(CONF)
        del conf['rsi']
        conf['rank'] = {'thresholds': [10, ]}
        self.assertEqual(self._call_cmd('-y', self._make_conf(conf)), 0)
        Popen.assert_called_with(['non_existent', '--dbpivot', 'rank,10'], 
                                 stdout=subprocess.PIPE)
        with open(data_f) as fp:
            expected = ['baz.bar.example.com,negative,True',
                        'foo.example.com,angel,True']
            for result, expect in zip(fp, expected):
                self.assertEqual(result.rstrip(), expect)
        with open(names_f) as fp:
            self.assertTrue(fp.read().startswith('class'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
