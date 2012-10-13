# -*- coding: utf-8 -*-

from vincetools.compat import unittest

class GroupByKeyTests(unittest.TestCase):

    def _run_it(self, iterable):
        from midas.tools import group_by_key
        return group_by_key(iterable)

    def test_general_case(self):
        data = ('{0}\t3'.format(e) for e in ['foo'] * 5 + ['bar'] * 3)
        result = [ list(block) for block in self._run_it(data) ]
        self.assertEqual(result, [['foo\t3']*5, ['bar\t3']*3])
        
    def test_single_key(self):
        result = [ list(block) for block in self._run_it(['foo\t3']*1) ]
        self.assertEqual(result, [['foo\t3']*1])
