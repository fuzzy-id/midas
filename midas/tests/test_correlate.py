# -*- coding: utf-8 -*-

from midas.tests import unittest

class BuildTreeTests(unittest.TestCase):

    def _run_it(self, sites):
        from midas.correlate import build_tree
        return build_tree(sites)

    def test_build_structure(self):
        tree = self._run_it(['foo.bar.com', 'baz.bar.com'])
        self.assertEqual(len(tree.branches), 1)
        com = tree.branches['com']
        self.assertEqual(len(com.branches), 1)
        bar = com.branches['bar']
        self.assertEqual(len(bar.branches), 2)
        foo = bar.branches['foo']
        self.assertEqual(len(foo.branches), 0)        
        self.assertEqual(foo.node_cnt, 1)
        baz = bar.branches['baz']
        self.assertEqual(len(baz.branches), 0)        
        self.assertEqual(baz.node_cnt, 1)

class ParentTests(unittest.TestCase):

    def _get_target_cls(self):
        from midas.correlate import Parent
        return Parent

    def test_add_value_on_last_node(self):
        obj = self._get_target_cls()('foo')
        obj.add_value('')
        obj.add_value('www')
        self.assertEqual(obj.values, ['', 'www'])
        
    def test_add_value_on_root(self):
        obj = self._get_target_cls()()
        obj.add_branch('foo.com')
        obj.add_value('com')
        obj.add_value('bar.baz')
        obj.add_value('foo.com')
        obj.add_value('www.foo.com')
        self.assertEqual(obj.values, ['bar.baz'])
        com = obj.branches['com']
        self.assertEqual(com.values, [''])
        foo = com.branches['foo']
        self.assertEqual(foo.values, ['', 'www'])

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
