# -*- coding: utf-8 -*-

from crawlcrunch.compat import comp_unicode
from crawlcrunch.tests import unittest

class BaseModelTests(unittest.TestCase):

    def _make_model(self, m):
        from crawlcrunch.helper import Model
        return Model(m)

class ModelTests(BaseModelTests):

    def test_equalitiy(self):
        a = self._make_model([])
        b = self._make_model([])
        self.assertTrue(a == b)

    def test_dynamic_attributes(self):
        a = self._make_model({'foo': list})
        b = self._make_model([int])
        setattr(a, 'foo', b)
        self.assertIs(a.foo, b)

class ModelCreationTests(BaseModelTests):

    def _run(self, obj):
        from crawlcrunch.helper import Model
        return Model.create_model(obj)

    def test_empty_dict(self):
        result = self._run({})
        expected = self._make_model({})
        self.assertEqual(result, expected)

    def test_empty_list(self):
        result = self._run([])
        expected = self._make_model([])
        self.assertEqual(result, expected)

    def test_unicode(self):
        result = self._run(comp_unicode('foo'))
        expected = self._make_model(str)
        self.assertEqual(result, expected)

    def test_none(self):
        result = self._run(None)
        expected = self._make_model(None)
        self.assertEqual(result, expected)

    def test_simple_dict(self):
        result = self._run({'foo': 'bar', })
        expected = self._make_model({'foo': str, })
        self.assertEqual(result, expected)

    def test_dict_with_list(self):
        result = self._run({'bar': ['foo', 8, 99.45],
                            'foo': []})
        expected = self._make_model({'bar': list,
                                   'foo': list})
        self.assertEqual(result, expected)

    def test_dict_with_none(self):
        result = self._run({'foo': None})
        expected = self._make_model({'foo': None})
        self.assertEqual(result, expected)

    def test_nested_dicts(self):
        result = self._run({'bar': {'foo': None,
                                    'bar': []}})
        expected = self._make_model({'bar': dict})
        self.assertEqual(result, expected)

    def test_not_implemented_class(self):
        with self.assertRaises(NotImplementedError):
            self._run(object())

class MergeModelTests(BaseModelTests):

    def _run(self, a, b):
        m_a = self._make_model(a)
        m_a.merge(self._make_model(b))
        return m_a

    def test_a_type_wins_none(self):
        result = self._run(None, list)
        self.assertEqual(result, self._make_model(list))
        result = self._run(list, None)
        self.assertEqual(result, self._make_model(list))

    def test_same_dictionaries(self):
        result = self._run({'foo': dict}, {'foo': dict})
        expected = self._make_model({'foo': dict})
        self.assertEqual(result, expected)

    def test_more_specific_type_in_dict_wins(self):
        result = self._run({'foo': None}, {'foo': list})
        expected = self._make_model({'foo': list})
        self.assertEqual(result, expected)
        result = self._run({'foo': list}, {'foo': None})
        self.assertEqual(result, expected)

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
        self.assertEqual(result, self._make_model([]))

    def test_tuple(self):
        result = self._run([int, int], [])
        expected = self._make_model([int, int])
        self.assertEqual(result, expected)
        result = self._run([], [int, int])
        self.assertEqual(result, expected)

    def test_list(self):
        result = self._run([str, str], [str, str, str])
        self.assertEqual(result, self._make_model([str]))

class ModelCreatorTests(BaseModelTests):

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
        self.assertEqual(mc.root, self._make_model({'foo': str}))
    
    def test_simple_list(self):
        mc = self._make_one((['foo', 'bar'], ['soot']))
        mc.run()
        self.assertEqual(mc.root, self._make_model([str]))

    def test_composed_obj_w_list(self):
        mc = self._make_one(({'foo': ['some', 'other']},
                             {'foo': ['one']},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, self._make_model({'foo': list}))
        self.assertEqual(mc.root.foo, self._make_model([str]))

    def test_composed_obj_w_dict(self):
        mc = self._make_one(({'foo': {'bar': 'other'}},
                             {'foo': {'bar': None}},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, self._make_model({'foo': dict}))
        self.assertEqual(mc.root.foo, self._make_model({'bar': str}))

    def test_composed_obj_w_tuple(self):
        mc = self._make_one(({'foo': [8, 10]},
                             {'foo': []},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, self._make_model({'foo': list}))
        self.assertEqual(mc.root.foo, self._make_model([int, int]))

if __name__ == '__main__': # pragma: no cover
    unittest.main()
