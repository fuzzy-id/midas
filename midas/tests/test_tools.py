# -*- coding: utf-8 -*-

from midas.compat import unittest

import midas.compat as vt_comp

import midas.tests as md_tests

class KeyFuncTestCase(unittest.TestCase):

    @property
    def _keyfunc(self):
        from midas.tools import get_key
        return get_key

    sequence = [ '{0}\tblah'.format(e) 
                 for e in ['foo'] * 5 + ['bar'] * 3 ]


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
        self.assertEqual(self._run_it(self.sequence),
                         dict([('foo', ['foo\tblah']*5),
                               ('bar', ['bar\tblah']*3)]))
                         

class RelationStatsTests(unittest.TestCase):

    def _run_it(self, iterable):
        from midas.tools import relation_stats
        return relation_stats(iterable)

    def test_stats_are_right(self):
        result = self._run_it(['foo', 'bar', 'baz', 'bar', 'foo'])
        self.assertEqual(result, (5, 3, 4, 2))

class MakePEmptyAttrTests(unittest.TestCase):

    def _make_obj_with_attr(self, attr_val):
        class Foo(object):
            attr = attr_val
        return Foo()

    def _run_it(self, o):
        from midas.tools import make_p_empty_attr
        predicate = make_p_empty_attr('attr')
        return predicate(o)

    def test_none_returns_true(self):
        o = self._make_obj_with_attr(None)
        self.assertTrue(self._run_it(o))

    def test_empty_str_returns_true(self):
        o = self._make_obj_with_attr('')
        self.assertTrue(self._run_it(o))

    def test_non_empty_str_returns_false(self):
        o = self._make_obj_with_attr('bar')
        self.assertFalse(self._run_it(o))

if __name__ == '__main__':  # pragma: no cover
    vt_comp.unittest.main()
