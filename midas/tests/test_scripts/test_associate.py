# -*- coding: utf-8 -*-

import operator
import os.path

from midas.compat import unittest
from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase
from midas.tests.test_scripts import IntegrationTestCase


class DomainTests(unittest.TestCase):

    def _run_it(self, company_or_site):
        from midas.scripts.associate import domain
        return domain(company_or_site)

    def test_on_site(self):
        self.assertEqual(self._run_it('example.com/foo'), 
                         'example.com')

    def test_on_object(self):
        with self.assertRaises(TypeError):
            self._run_it(object())

    def test_on_full_url(self):
        result = self._run_it('http://example.com/foo')
        self.assertEqual(result, 'example.com')


class AssociationTreeTests(unittest.TestCase):

    def _get_target_cls(self):
        from midas.scripts.associate import AssociationTree
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
        result = list(map(operator.attrgetter('name'), 
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
        from midas.scripts.associate import split_domain
        return split_domain(s)

    def test_on_empty_str(self):
        self.assertEqual(self._run_it(''), ('', ))


class AssociateOnTestDataTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.associate import Associate
        return Associate

    def test_on_data(self):
        self._call_cmd(TEST_DATA_PATH['site_count'], TEST_DATA_PATH['companies'])
        self.assert_stdout_equal('\n'.join(['baz-bar\tbaz.bar.example.com/path',
                                            'foo\tfoo.example.com', 
                                            '']))


class AssociateOnConstructedDataTests(IntegrationTestCase):

    def _get_target_cls(self):
        from midas.scripts.associate import Associate
        return Associate

    def test_companies_with_same_sites_are_rejected(self):
        companies = os.path.join(self.tmpd, 'companies')
        with open(companies, 'w') as fp:
            fp.writelines('\n'.join(['bar\thttp://example.com/bar\ta\t2013-01-12',
                                     'foo\thttp://example.com/foo\ta\t2013-01-12',
                                     '']))
        site_count = os.path.join(self.tmpd, 'site_count')
        with open(site_count, 'w') as fp:
            fp.write('example.com\t1\n')
        self.assertEqual(self._call_cmd(site_count, companies), 0)
        self.assert_stdout_equal('')

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
