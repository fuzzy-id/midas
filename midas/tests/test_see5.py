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
