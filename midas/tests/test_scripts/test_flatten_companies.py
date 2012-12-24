# -*- coding: utf-8 -*-

from midas.compat import unittest

from midas.tests.test_scripts import IntegrationTestCaseNG
from midas.tests import TEST_DATA_PATH

class FlattenCompaniesTests(IntegrationTestCaseNG):

    def _get_target_cls(self):
        from midas.scripts.flatten_companies import FlattenCompanies
        return FlattenCompanies

    def test_on_test_data(self):
        self.assertEqual(
            self._call_cmd(TEST_DATA_PATH['crunchbase_companies']), 
            0
            )
        self.assert_cls_out_equal(
            ''.join(['baz-bar\thttp://baz.bar.example.com/\tangel\t2012-12-01\n',
                     'foo\thttp://foo.example.com/\tangel\t2012-12-01\n'])
            )
