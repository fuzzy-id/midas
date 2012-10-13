# -*- coding: utf-8 -*-

from vincetools.compat import unittest

class KeyFuncTestCase(unittest.TestCase):

    @property
    def _keyfunc(self):
        from midas.tools import get_key
        return get_key

    sequence = [ '{0}\tblah'.format(e) 
                 for e in ['foo'] * 5 + ['bar'] * 3 ]


class GroupByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import group_by_key
        return [ list(block) 
                 for block in group_by_key(iterable, self._keyfunc) ]

    def test_on_empty_sequence(self):
        self.assertEqual([], self._run_it([]))

    def test_on_sequence(self):
        self.assertEqual([['foo\tblah']*5, ['bar\tblah']*3], 
                         self._run_it(self.sequence))
        
    def test_single_key(self):
        result = [ list(block) for block in self._run_it(['foo\t3']*1) ]
        self.assertEqual([['foo\t3']*1], result)


class CountByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import count_by_key
        return count_by_key(iterable, self._keyfunc)

    def test_on_empty_sequence(self):
        self.assertEqual(dict(), self._run_it([]))

    def test_on_sequence(self):
        self.assertEqual(dict([('foo', 5), 
                               ('bar', 3)]),
                         self._run_it(self.sequence))


class CollectByKeyTests(KeyFuncTestCase):

    def _run_it(self, iterable):
        from midas.tools import collect_by_key
        return collect_by_key(iterable, self._keyfunc)

    def test_on_empty_sequence(self):
        self.assertEqual(dict(), self._run_it([]))

    def test_on_sequence(self):
        self.assertEqual(dict([('foo', ['foo\tblah']*5),
                               ('bar', ['bar\tblah']*3)]), 
                         self._run_it(self.sequence))
