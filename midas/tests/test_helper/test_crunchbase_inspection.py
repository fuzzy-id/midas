# -*- coding: utf-8 -*-

from midas.compat import comp_unicode
from midas.compat import unittest


class BaseModelTests(unittest.TestCase):

    def _get_target_class(self):
        from midas.helper.crunchbase_inspection import Model
        return Model

    def _make_model(self, m):
        return self._get_target_class()(m)


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

    def test_repr(self):
        result = repr(self._make_model(str))
        expected = 'Model( ' + str(str) + ' )'
        self.assertEqual(result, expected)

    def test_str(self):
        result = str(self._make_model(str))
        expected = str(str)
        self.assertEqual(result, expected)

    def test_equality_with_other_instance(self):
        self.assertFalse(self._make_model(str) == str)


class CreateModelTests(BaseModelTests):

    def _create_model(self, obj):
        return self._get_target_class().create_model(obj)

    def test_empty_dict(self):
        result = self._create_model({})
        expected = self._make_model({})
        self.assertEqual(result, expected)

    def test_empty_list(self):
        result = self._create_model([])
        expected = self._make_model([])
        self.assertEqual(result, expected)

    def test_unicode(self):
        result = self._create_model(comp_unicode('foo'))
        expected = self._make_model(str)
        self.assertEqual(result, expected)

    def test_none(self):
        result = self._create_model(None)
        expected = self._make_model(None)
        self.assertEqual(result, expected)

    def test_simple_dict(self):
        result = self._create_model({'foo': 'bar', })
        expected = self._make_model({'foo': str, })
        self.assertEqual(result, expected)

    def test_dict_with_list(self):
        result = self._create_model({'bar': ['foo', 8, 99.45],
                                     'foo': []})
        expected = self._make_model({'bar': list,
                                     'foo': list})
        self.assertEqual(result, expected)

    def test_dict_with_none(self):
        result = self._create_model({'foo': None})
        expected = self._make_model({'foo': None})
        self.assertEqual(result, expected)

    def test_nested_dicts(self):
        result = self._create_model({'bar': {'foo': None,
                                             'bar': []}})
        expected = self._make_model({'bar': dict})
        self.assertEqual(result, expected)

    def test_not_implemented_class(self):
        with self.assertRaises(NotImplementedError):
            self._create_model(object())


class MergeModelTests(BaseModelTests):

    def _merge_models(self, a, b):
        m_a = self._make_model(a)
        m_a.merge(self._make_model(b))
        return m_a

    def test_a_type_wins_none(self):
        result = self._merge_models(None, list)
        self.assertEqual(result, self._make_model(list))
        result = self._merge_models(list, None)
        self.assertEqual(result, self._make_model(list))

    def test_same_dictionaries(self):
        result = self._merge_models({'foo': dict}, {'foo': dict})
        expected = self._make_model({'foo': dict})
        self.assertEqual(result, expected)

    def test_more_specific_type_in_dict_wins(self):
        result = self._merge_models({'foo': None}, {'foo': list})
        expected = self._make_model({'foo': list})
        self.assertEqual(result, expected)
        result = self._merge_models({'foo': list}, {'foo': None})
        self.assertEqual(result, expected)

    def test_different_keys_raise_error(self):
        with self.assertRaises(ValueError):
            self._merge_models({'foo': int}, {'foo': int, 'bar': str})
        with self.assertRaises(ValueError):
            self._merge_models({'foo': int, 'bar': str}, {'foo': int})

    def test_different_objects_raise_error(self):
        with self.assertRaises(TypeError):
            self._merge_models(list(), dict())

    def test_not_implemented_class(self):
        with self.assertRaises(NotImplementedError):
            self._merge_models(object(), object())

    def test_empty_list(self):
        result = self._merge_models([], [])
        self.assertEqual(result, self._make_model([]))

    def test_tuple(self):
        result = self._merge_models([float, float], [])
        expected = self._make_model([float, float])
        self.assertEqual(result, expected)
        result = self._merge_models([], [float, float])
        self.assertEqual(result, expected)

    def test_list(self):
        result = self._merge_models([str, str], [str, str, str])
        self.assertEqual(result, self._make_model([str]))

    def test_list_with_different_objects(self):
        with self.assertRaises(ValueError):
            self._merge_models([int], [int, float])


class ModelInspectorTests(BaseModelTests):

    def __get_target_class(self):
        from midas.helper.crunchbase_inspection import ModelInspector
        return ModelInspector

    def _make_one(self, obj_iter, root_access=(lambda x: x)):
        return self.__get_target_class()(obj_iter, root_access)

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

    def test_empty_lists(self):
        mc = self._make_one(([], [], []))
        mc.run()
        self.assertEqual(mc.root, self._make_model([]))

    def test_mostly_empty_lists(self):
        mc = self._make_one(([], [8], []))
        mc.run()
        self.assertEqual(mc.root, self._make_model([int]))

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
        mc = self._make_one(({'foo': [8.7, 10]},
                             {'foo': []},
                             {'foo': None}))
        mc.run()
        self.assertEqual(mc.root, self._make_model({'foo': list}))
        self.assertEqual(mc.root.foo, self._make_model([float, int]))

    def test_lists_with_dicts_inside(self):
        mc = self._make_one(([{'foo': None}, {'foo': 8}],
                             [{'foo': 70}],
                             []))
        mc.run()
        self.assertEqual(mc.root, self._make_model([dict]))
        self.assertEqual(mc.root.list, self._make_model({'foo': int}))

    def test_list_with_lists_inside(self):
        mc = self._make_one(([[8, 9], [90, 0]],
                             [], [[1, 2]]))
        mc.run()
        self.assertEqual(mc.root, self._make_model([list]))
        self.assertEqual(mc.root.list, self._make_model([int, int]))

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
