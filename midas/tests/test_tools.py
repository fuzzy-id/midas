# -*- coding: utf-8 -*-

from vincetools.compat import unittest

from midas.tests import SITE_COUNT
from midas.tests import ConfiguredDBTestCase

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
        self.assertEqual(self._run_it(self.sequence),
                         dict([('foo', ['foo\tblah']*5),
                               ('bar', ['bar\tblah']*3)]))
                         

class DomainTests(unittest.TestCase):

    def _run_it(self, company_or_site):
        from midas.tools import domain
        return domain(company_or_site)

    def test_on_company(self):
        from midas.tools import Company
        c = Company(homepage_url='http://example.com/foo')
        self.assertEqual(self._run_it(c), 'example.com')

    def test_on_site(self):
        self.assertEqual(self._run_it('example.com/foo'), 
                         'example.com')

    def test_on_object(self):
        with self.assertRaises(TypeError):
            self._run_it(object())


class IterCompaniesTests(ConfiguredDBTestCase):

    def _run_it(self):
        from midas.tools import iter_all_companies
        return list(iter_all_companies())

    def test_iter_all_companies(self):
        c1 = self._make_company_json({})
        c2 = self._make_company_json({})
        self.assertEqual(self._run_it(), [c1, c2])


class IterInteresstingCompaniesTests(ConfiguredDBTestCase):

    def _run_it(self):
        from midas.tools import iter_interesting_companies
        return list(iter_interesting_companies())

    def test_function_runs(self):
        c = self._make_company_json({})
        self.assertEqual(self._run_it(), [])


class IterSitesCountTests(ConfiguredDBTestCase):

    def test_iter_site_counts(self):
        from midas.tools import iter_site_counts
        result = list(iter_site_counts())
        self.assertEqual((result[0].site, result[0].count), SITE_COUNT[1][0])
        self.assertEqual((result[1].site, result[1].count), SITE_COUNT[1][1])

    def test_iter_all_sites(self):
        from midas.tools import iter_all_sites
        result = list(iter_all_sites())
        self.assertEqual(result, [SITE_COUNT[1][0][0], SITE_COUNT[1][1][0]])

    def test_iter_interesting_sites(self):
        from midas.tools import iter_interesting_sites
        result = list(iter_interesting_sites())
        self.assertEqual(result, [SITE_COUNT[1][0][0]])
