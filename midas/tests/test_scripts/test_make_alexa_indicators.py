# -*- coding: utf-8 -*-

from midas.compat import unittest
from midas.tests.test_scripts import MDCommandTestCase

class ExpandArgumentsTests(unittest.TestCase):

    def _get_target(self):
        from midas.scripts.make_alexa_indicators import expand_arguments
        return expand_arguments

    def test_start_stop_step_on_ndays_and_threshold(self):
        func = self._get_target()
        result = func({'rsi': {'ndays': {'start': 0,
                                         'stop': 3,
                                         'step': 2},
                               'threshold': {'start': 0,
                                             'stop': 2}}})
        expected = [('rsi', 0, 0), ('rsi', 0, 1), ('rsi', 2, 0), ('rsi', 2, 1)]
        self.assertEqual(result, expected)

    def test_list_on_ndays_and_threshold(self):
        func = self._get_target()
        result = func({'rsi': {'ndays': [0, 1],
                               'threshold': [0, 2]}})
        expected = [('rsi', 0, 0), ('rsi', 0, 1), ('rsi', 2, 0), ('rsi', 2, 1)]
        self.assertEqual(result, expected)
