# -*- coding: utf-8 -*-

from midas.tests import TEST_DATA
from midas.tests import IntegrationTestCase
from vincetools.compat import unittest

class AlexaToNamesAndOneTests(IntegrationTestCase):

    def _run_it(self, *args):
        effargs = ['alexa_to_names_and_one']
        effargs.extend(args)
        from midas.scripts.alexa_count_names import AlexaToNamesAndOne
        return AlexaToNamesAndOne.cmd(effargs)

    def test_on_file(self):
        ret_code = self._run_it('-q', TEST_DATA[0])
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal(''.join('{0}\t1\n'.format(e.site)
                                         for e in TEST_DATA[1]))

class SumValues(IntegrationTestCase):

    def _run_it(self, *args):
        effargs = ['md_sum_values']
        effargs.extend(args)
        from midas.scripts.alexa_count_names import SumValues
        return SumValues.cmd(effargs)

    def test_simple(self):
        ret_code = self._run_it(*('{0}\t1\n'.format(name) 
                                  for name in ['foo'] * 5 + ['bar'] * 3))
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal('foo\t5\nbar\t3\n')
