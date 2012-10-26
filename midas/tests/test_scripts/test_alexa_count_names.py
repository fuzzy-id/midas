# -*- coding: utf-8 -*-

from midas.tests import TEST_ALEXA_TOP1M
from midas.tests import TEST_ALEXA_TOP1M_FILES
from midas.tests.test_scripts import IntegrationTestCase

class AlexaToNamesAndOneTests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.alexa_count_names import AlexaToNamesAndOne
        return AlexaToNamesAndOne.cmd

    def test_on_file(self):
        ret_code = self._run_it('-q', *TEST_ALEXA_TOP1M_FILES)
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal(''.join('{0}\t1\n'.format(e.site)
                                         for e in TEST_ALEXA_TOP1M))

class SumValues(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.alexa_count_names import SumValues
        return SumValues.cmd

    def test_simple(self):
        ret_code = self._run_it(*('{0}\t1\n'.format(name) 
                                  for name in ['foo'] * 5 + ['bar'] * 3))
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal('foo\t5\nbar\t3\n')
