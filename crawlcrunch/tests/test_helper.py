# -*- coding: utf-8 -*-

from crawlcrunch.compat import comp_unicode
from crawlcrunch.tests import unittest

class DetermineTypeTests(unittest.TestCase):

    def _run(self, obj):
        from crawlcrunch.helper import determine_type_flat
        return determine_type_flat(obj)

    def test_empty_dict(self):
        result = self._run({})
        self.assertEqual(result, {})

    def test_empty_list(self):
        result = self._run([])
        self.assertEqual(result, [])

    def test_unicode(self):
        result = self._run(comp_unicode('foo'))
        self.assertEqual(result, str)

    def test_none(self):
        result = self._run(None)
        self.assertEqual(result, None)

    def test_simple_dict(self):
        result = self._run({'foo': 'bar', })
        self.assertEqual(result, {'foo': str, })

    def test_dict_with_list(self):
        result = self._run({'bar': ['foo', 8, 99.45],
                            'foo': []})
        self.assertEqual(result, {'bar': list,
                                  'foo': list})

    def test_dict_with_none(self):
        result = self._run({'foo': None})
        self.assertEqual(result, {'foo': None})

    def test_nested_dicts(self):
        result = self._run({'bar': {'foo': None,
                                    'bar': []}})
        self.assertEqual(result, {'bar': dict})

    def test_not_implemented_class(self):
        with self.assertRaises(NotImplementedError):
            self._run(object())

class MergeTypeDescriptionTests(unittest.TestCase):

    def _run(self, a, b):
        from crawlcrunch.helper import merge_type_descr
        return merge_type_descr(a, b)

    def test_a_type_wins_none(self):
        result = self._run(None, list)
        self.assertEqual(result, list)
        result = self._run(list, None)
        self.assertEqual(result, list)

    def test_same_dictionaries(self):
        result = self._run({'foo': dict}, {'foo': dict})
        self.assertEqual(result, {'foo': dict})

    def test_more_specific_type_in_dict_wins(self):
        result = self._run({'foo': None}, {'foo': list})
        self.assertEqual(result, {'foo': list})
        result = self._run({'foo': list}, {'foo': None})
        self.assertEqual(result, {'foo': list})

    def test_different_keys_raise_error(self):
        with self.assertRaises(ValueError):
            self._run({'foo': int}, {'foo': int, 'bar': str})
        with self.assertRaises(ValueError):
            self._run({'foo': int, 'bar': str}, {'foo': int})

    def test_different_objects_raise_error(self):
        with self.assertRaises(TypeError):
            self._run(list(), dict())
        
    def test_not_implemented_class(self):
        with self.assertRaises(NotImplementedError):
            self._run(object(), object())

    def test_empty_list(self):
        result = self._run([], [])
        self.assertEqual(result, [])

    def test_tuple(self):
        result = self._run([int, int], [])
        self.assertEqual(result, [int, int])
        result = self._run([], [int, int])
        self.assertEqual(result, [int, int])

    def test_list(self):
        result = self._run([str, str], [str, str, str])
        self.assertEqual(result, [str])

class ModelCreatorTests(unittest.TestCase):

    def _make_one(self, obj_iter, root_access=(lambda x: x)):
        from crawlcrunch.helper import ModelCreator
        return ModelCreator(obj_iter, root_access)

    def test_make_access_function(self):
        mc = self._make_one(None)
        func = mc.make_access_function('foo')
        result = func({'foo': ['some', 'bar']})
        self.assertEqual(result, ['some', 'bar'])

    def test_simple_dict(self):
        mc = self._make_one(({'foo': 'bar'},
                             {'foo': 'some'}))
        mc.run()
        self.assertEqual(mc.root, {'foo': str})
    
    def test_simple_list(self):
        mc = self._make_one((['foo', 'bar'], ['soot']))
        mc.run()
        self.assertEqual(mc.root, [str])

    def test_composed_obj_w_list(self):
        mc = self._make_one(({'foo': ['some', 'other']},
                             {'foo': ['one']},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, {'foo': list})
        self.assertEqual(mc.foo, [str])

    def test_composed_obj_w_dict(self):
        mc = self._make_one(({'foo': {'bar': 'other'}},
                             {'foo': {'bar': None}},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, {'foo': dict})
        self.assertEqual(mc.foo, {'bar': str})

    def test_composed_obj_w_tuple(self):
        mc = self._make_one(({'foo': [8, 10]},
                             {'foo': []},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, {'foo': list})
        self.assertEqual(mc.foo, [int, int]})

if __name__ == '__main__': # pragma: no cover
    unittest.main()
