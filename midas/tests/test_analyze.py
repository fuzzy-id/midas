# -*- coding: utf-8 -*-

from midas.tests import TEST_DATA
from midas.tests import IntegrationTestCase
from midas.tests import unittest

class AlexaToNamesAndOneTests(IntegrationTestCase):

    def _run_it(self, *args):
        effargs = ['alexa_to_names_and_one']
        effargs.extend(args)
        from midas.analyze import run_alexa_to_names_and_one
        return run_alexa_to_names_and_one(effargs)

    def test_on_file(self):
        ret_code = self._run_it(TEST_DATA[0])
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal(''.join('{0}\t1\n'.format(e.name)
                                         for e in TEST_DATA[1]))

class SumValues(IntegrationTestCase):

    def _run_it(self, *args):
        effargs = ['md_sum_values']
        effargs.extend(args)
        from midas.analyze import run_sum_names
        return run_sum_names(effargs)

    def test_simple(self):
        ret_code = self._run_it(*('{0}\t1\n'.format(name) 
                                  for name in ['foo'] * 5 + ['bar'] * 3))
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal('foo\t5\nbar\t3\n')

class GetInBlocksTests(unittest.TestCase):

    def _run_it(self, iterable):
        from midas.analyze import group_by_key
        return group_by_key(iterable)

    def test_general_case(self):
        data = ('{0}\t3'.format(e) for e in ['foo'] * 5 + ['bar'] * 3)
        result = [ list(block) for block in self._run_it(data) ]
        self.assertEqual(result, [['foo\t3']*5, ['bar\t3']*3])
        
    def test_single_key(self):
        result = [ list(block) for block in self._run_it(['foo\t3']*1) ]
        self.assertEqual(result, [['foo\t3']*1])
                   
