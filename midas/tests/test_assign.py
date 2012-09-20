# -*- coding: utf-8 -*-

import sys

from midas.tests import IntegrationTestCase

class FindStrangNamesTests(IntegrationTestCase):

    def _run_test(self, sites):
        from midas.assign import find_strange_names
        _in = '\t1900-01-01, 2\n'.join(sites)
        sys.stdin.write(_in)
        sys.stdin.seek(0)
        result = find_strange_names()
        sys.stdout.seek(0)
        return result, sys.stdout.getvalue()

    def test_normal_names(self):
        sites = ['foo.example',
                 'bar.sub.example',
                 'example.com', '']
        result, out = self._run_test(sites)
        self.assertEqual(result, 0)
        self.assertEqual(out, '')

    def test_names_with_slashes(self):
        sites = ['http://foo.example',
                 'bar.example/',
                 'example.com/query', '']
        result, out = self._run_test(sites)
        self.assertEqual(result, 0)
        self.assertEqual(out, '\n'.join(sites))
