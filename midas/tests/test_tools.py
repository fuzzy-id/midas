# -*- coding: utf-8 -*-

from vincetools.compat import unittest

class KeyFuncTestCase(unittest.TestCase):

    @property
    def _keyfunc(self):
        from midas.tools import get_key
        return get_key


class GroupByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable, keyfunc=None):
        from midas.tools import group_by_key
        return group_by_key(iterable, self._keyfunc)

    def test_general_case(self):
        data = ('{0}\t3'.format(e) for e in ['foo'] * 5 + ['bar'] * 3)
        result = [ list(block) for block in self._run_it(data) ]
        self.assertEqual(result, [['foo\t3']*5, ['bar\t3']*3])
        
    def test_single_key(self):
        result = [ list(block) for block in self._run_it(['foo\t3']*1) ]
        self.assertEqual(result, [['foo\t3']*1])

class CountByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import count_by_key
        return count_by_key(iterable, self._keyfunc)

    def test_on_empty_sequence(self):
        self.assertEqual(dict(), self._run_it([]))

    def test_on_sequence(self):
        sequence = [ '{0}\tblah'.format(key)
                     for key in ['foo']*2 + ['bar']*1 ]
        self.assertEqual(dict([('foo', 2), 
                               ('bar', 1)]),
                         self._run_it(sequence))

