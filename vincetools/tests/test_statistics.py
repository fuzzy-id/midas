# -*- coding: utf-8 -*-

from vincetools.compat import unittest

class TopItemsTests(unittest.TestCase):

    def _run_it(self, iterable, keyfunc, **kwargs):
        from vincetools.statistics import top_items
        return top_items(iterable, keyfunc, **kwargs)

    def test_empty_iterable(self):
        self.assertEqual(self._run_it([], lambda x: x),
                         [])
        
    def test_on_a_dict(self):
        data = dict((i, list(range(i))) 
                    for i in range(5))
        keyfunc = lambda k: len(data[k])
        result = self._run_it(data, keyfunc, n=3)
        self.assertEqual(result, [(i, i)
                                  for i in range(4, 1, -1)])
