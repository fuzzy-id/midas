# -*- coding: utf-8 -*-

import os.path

from midas.compat import unittest

from midas.tests.test_scripts import IntegrationTestCase
from midas.tests import TEST_DATA_PATH

class FlattenCompaniesTests(IntegrationTestCase):

    def _get_target_cls(self):
        from midas.scripts.flatten_companies import FlattenCompanies
        return FlattenCompanies

    def test_on_test_data(self):
        with open(os.path.join(TEST_DATA_PATH['crunchbase_companies'],
                               'baz-bar.json')) as fp:
            self.stdin.write(fp.read())
        self.stdin.write('\n')
        with open(os.path.join(TEST_DATA_PATH['crunchbase_companies'],
                               'foo.json')) as fp:
            self.stdin.write(fp.read())
        self.stdin.write('\n')
        self.assertEqual(self._call_cmd(), 0)
        self.assert_stdout_equal(
            ''.join(['baz-bar\thttp://baz.bar.example.com/\tangel\t2012-12-01\n',
                     'foo\thttp://foo.example.com/\tangel\t2012-12-01\n'])
            )
