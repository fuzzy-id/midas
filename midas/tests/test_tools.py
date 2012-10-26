# -*- coding: utf-8 -*-

from vincetools.compat import unittest

from midas.tests import TEST_SITE_COUNT
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
        from crawlcrunch.model.db import Company
        c = Company(homepage_url='http://example.com/foo')
        self.assertEqual(self._run_it(c), 'example.com')

    def test_on_site(self):
        self.assertEqual(self._run_it('example.com/foo'), 
                         'example.com')

    def test_on_object(self):
        with self.assertRaises(TypeError):
            self._run_it(object())

    def test_on_full_url(self):
        result = self._run_it('http://example.com/foo')
        self.assertEqual(result, 'example.com')

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

    def test_company_w_two_funding_rounds_is_returned_once(self):
        c = self._make_company_json(self.companies_js[0])
        self.assertEqual(self._run_it(), [c])


class IterSitesCountTests(ConfiguredDBTestCase):

    def test_iter_site_counts(self):
        from midas.tools import iter_site_counts
        result = list(iter_site_counts())
        self.assertEqual(result, TEST_SITE_COUNT)

    def test_iter_all_sites(self):
        from midas.tools import iter_all_sites
        result = list(iter_all_sites())
        self.assertEqual(result,
                         [ sc.site for sc in TEST_SITE_COUNT ])

    def test_iter_interesting_sites(self):
        from midas.tools import iter_interesting_sites
        result = list(iter_interesting_sites())
        self.assertEqual(result, ['foo.example.com'])

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
