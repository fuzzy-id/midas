# -*- coding: utf-8 -*-

import operator

from midas.compat import unittest
from midas.tests import TEST_DATA_PATH
from midas.tests.test_scripts import MDCommandTestCase


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


class AssociateTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts.associate import Associate
        return Associate

    def test_on_data(self):
        self._call_cmd(TEST_DATA_PATH['site_count'], TEST_DATA_PATH['companies'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
