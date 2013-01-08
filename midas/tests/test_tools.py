# -*- coding: utf-8 -*-

import os.path

import midas

from midas.compat import unittest

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


class IterFilesContentTests(unittest.TestCase):

    def _get_target(self):
        from midas.tools import iter_files_content
        return iter_files_content

    def test_on_site_count(self):
        path_pattern = os.path.join(md_tests.TEST_DATA_PATH['site_count'], 
                                    'data')
        func = self._get_target()
        result = [ line for line in func(path_pattern) ]
        with open(path_pattern) as fp:
            expected = fp.readlines()
        self.assertEqual(result, expected)
            

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
