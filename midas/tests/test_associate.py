# -*- coding: utf-8 -*-

import operator

from vincetools.compat import imap
from vincetools.compat import unittest
from midas.tests import ConfiguredDBTestCase

class AssociationTreeTests(unittest.TestCase):

    def _get_target_cls(self):
        from midas.associate import AssociationTree
        return AssociationTree

    def _make_one(self, split_func=lambda s: s.split('.', 1)):
        return self._get_target_cls()(split_func)

    def test_single_root(self):
        root = self._make_one()
        self.assertEqual(len(root), 0)

    def test_grow_branch(self):
        root = self._make_one()
        root.grow('foo-item', 'foo')
        self.assertEqual(len(root.leafs), 0)
        self.assertEqual(len(root), 1)
        self.assertEqual(root['foo'].leafs, ['foo-item'])
        self.assertEqual(len(root['foo']), 0)

    def test_associate(self):
        root = self._make_one()
        root.grow('foo.bar-branch', 'foo.bar')
        root.grow('foo.baz.blup-branch', 'foo.baz.blup')
        self.assertEqual(root.associate('foo'), None)
        self.assertEqual(root.associate('foo.bar'), ['foo.bar-branch'])
        self.assertEqual(root.associate('foo.bar.baz'), ['foo.bar-branch'])
        self.assertEqual(root.associate('foo.baz'), ['foo.baz.blup-branch'])

    def test_query(self):
        root = self._make_one()
        root.grow('foo.bar-branch', 'foo.bar')
        result = list(imap(operator.attrgetter('name'), 
                           root.query(lambda n: len(n.leafs) > 0)))
        self.assertEqual(result, ['bar'])

    def test_map(self):
        root = self._make_one()
        root.grow('foo.bar-branch', 'foo.bar')
        root.grow('foo.baz-branch', 'foo.baz')
        result = root.map(['foo', 'foo.bar'])
        self.assertEqual(result, {'foo.bar': ['foo.bar-branch']})

class SplitDomainTests(unittest.TestCase):

    def _run_it(self, s):
        from midas.associate import split_domain
        return split_domain(s)

    def test_on_empty_str(self):
        self.assertEqual(self._run_it(''), ('', ))

class AssociateSitesToCompaniesTests(ConfiguredDBTestCase):

    def _run_it(self, iterable=None):
        from midas.associate import associate_sites_to_companies
        return associate_sites_to_companies(iterable)

    def test_on_test_config(self):
        foo_comp = self._make_company_json(self.companies_js[0])
        bar_comp = self._make_company_json(self.companies_js[1])
        self.assertEqual(self._run_it(), 
                         {foo_comp: ['foo.example.com']})


class AssociateCompaniesToSitesTests(ConfiguredDBTestCase):

    def _run_it(self, iterable=None):
        from midas.associate import associate_companies_to_sites
        return associate_companies_to_sites(iterable)

    def test_on_test_config(self):
        foo_comp = self._make_company_json(self.companies_js[0])
        bar_comp = self._make_company_json(self.companies_js[1])
        self.assertEqual(self._run_it(), 
                         {'foo.example.com': [foo_comp]})

class AssociationTests(ConfiguredDBTestCase):
    " Test the proper working of the Association class. "

    def test_backref_on_company(self):
        foo_comp = self._make_company_json(self.companies_js[0])
        from midas.associate import Association
        assoc = Association(site='foo.example.com', company=foo_comp)
        result = self.session.query(Association).one()
        self.assertIs(result, assoc)
        from crawlcrunch.model.db import Company
        result = self.session.query(Company).one()
        self.assertIs(result.site, assoc)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
