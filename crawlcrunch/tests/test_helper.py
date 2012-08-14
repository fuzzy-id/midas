# -*- coding: utf-8 -*-

from crawlcrunch.tests import unittest

class DetermineTypeTests(unittest.TestCase):

    def _run(self, obj):
        from crawlcrunch.helper import determine_type
        return determine_type(obj)

    def test_empty_dict(self):
        result = self._run({})
        self.assertEqual(result, {})

    def test_empty_list(self):
        result = self._run([])
        self.assertEqual(result, [])

    def test_none(self):
        result = self._run(None)
        self.assertEqual(result, None)

    def test_simple_dict(self):
        result = self._run({'foo': 'bar', })
        self.assertEqual(result, {'foo': str, })

    def test_dict_with_list(self):
        result = self._run({'bar': ['foo', 8, 99.45],
                                 'foo': []})
        self.assertEqual(result, {'bar': [str, int, float],
                                  'foo': []})

    def test_nested_dicts(self):
        result = self._run({'bar': {'foo': None,
                                    'bar': []}})
        self.assertEqual(result, {'bar': {'foo': None,
                                          'bar': []}})
