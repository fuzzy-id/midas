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

    def test_nested_dicts(self):
        result = self._run({'bar': {'foo': None,
                                    'bar': []}})
        self.assertEqual(result, {'bar': dict})

    def test_not_implemented_class(self):
        with self.assertRaises(NotImplementedError):
            self._run(object())
