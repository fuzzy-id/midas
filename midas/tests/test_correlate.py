# -*- coding: utf-8 -*-

from midas.tests import unittest

class BucketTreeTests(unittest.TestCase):

    def _get_target_cls(self):
        from midas.correlate import BucketTree
        return BucketTree

    def _make_one(self, split_func=lambda s: s.split('.', 1)):
        return self._get_target_cls()(split_func)

    def test_single_root(self):
        root = self._make_one()
        self.assertEqual(len(root), 0)
        self.assertEqual(len(root.bucket), 0)

    def test_grow_branch(self):
        root = self._make_one()
        root.grow('foo-item', 'foo')
        self.assertEqual(len(root.leafs), 0)
        self.assertEqual(len(root), 1)
        self.assertEqual(root['foo'].leafs, ['foo-item'])
        self.assertEqual(len(root['foo']), 0)

    def test_fill_single_root(self):
        root = self._make_one()
        root.fill('www', None)
        self.assertEqual(root.bucket[None], ['www'])

    def test_fill_not_existing_branch(self):
        root = self._make_one()
        root.fill('foo-item', 'foo')
        self.assertEqual(root.bucket['foo'], ['foo-item'])

    def test_fill_grown_branch(self):
        root = self._make_one()
        root.grow('foo-branch', 'foo')
        root.fill('foo-item', 'foo')
        root.fill('foo.bar-item', 'foo.bar')
        self.assertIn('foo', root)
        self.assertEqual(len(root.bucket), 0)
        self.assertEqual(len(root['foo'].bucket), 2)
        self.assertEqual(root['foo'].bucket['bar'], ['foo.bar-item'])
        self.assertEqual(root['foo'].bucket[None], ['foo-item'])

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
