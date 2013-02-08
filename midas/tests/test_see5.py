# -*- coding: utf-8 -*-

from midas.compat import unittest

class GetClassifiedTableTests(unittest.TestCase):

    def _get_target(self):
        from midas.see5 import get_classified_table
        return get_classified_table

    def test_on_simple_table(self):
        s = '\n'.join(
            ['           (a)   (b)    <-classified as',
             '          ----  ----',
             '         10062   833    (a): class False',
             '          1005    87    (b): class True']
            )
        expected = {'False': {'False': 10062, 'True': 833},
                    'True': {'False': 1005, 'True': 87}}
        result = self._get_target()(s)
        self.assertEqual(result, expected)

    def test_empty_fields(self):
        s = '\n'.join(
            ['           (a)   (b)    <-classified as',
             '          ----  ----',
             '         10062          (a): class False',
             '          1005          (b): class True']
            )
        expected = {'False': {'False': 10062, 'True': 0},
                    'True': {'False': 1005, 'True': 0}}
        result = self._get_target()(s)
        self.assertEqual(result, expected)

    def test_parsing_with_sample(self):
        s = '\n'.join(
            ['Evaluation on training data (9590 cases):',
             '',
             '               Decision Tree       ',
             '          -----------------------  ',
             '          Size      Errors   Cost  ',
             '',
             '           261 2505(26.1%)   0.37   <<',
             '',
             '',
             '           (a)   (b)    <-classified as',
             '          ----  ----',
             '          6340  2378    (a): class False',
             '           127   745    (b): class True',
             '',
             '',
             '        Attribute usage:',
             '',
             '            100%  spearman_60_0.60',
             '             98%  rank_20000',
             '             63%  spearman_45_0.60',
             '             57%  spearman_15_1.00',
             '',
             '',
             'Evaluation on test data (2397 cases):',
             '',
             '               Decision Tree       ',
             '          -----------------------  ',
             '          Size      Errors   Cost  ',
             '',
             '           261  851(35.5%)   0.80   <<',
             '',
             '',
             '           (a)   (b)    <-classified as',
             '          ----  ----',
             '          1458   719    (a): class False',
             '           132    88    (b): class True',]
            )
        expected = {'False': {'False': 1458, 'True': 719},
                    'True': {'False': 132, 'True': 88}}
        result = self._get_target()(s)
        self.assertEqual(result, expected)
