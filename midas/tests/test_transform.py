# -*- coding: utf-8 -*-

import sys

import mock

from midas.compat import StringIO
from midas.tests import TEST_DATA
from midas.tests import IntegrationTestCase

class AlexaToSha1Tests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.transform import alexa_to_sha1
        return alexa_to_sha1

    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')

    def test_on_test_data(self):
        ret_code = self._run('-q', TEST_DATA[0])
        self.assertEqual(ret_code, 0)
        self.assert_stdout_equal('\n'.join(e.format_w_key 
                                           for e in TEST_DATA[1]) + '\n')


class SortSha1Tests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.transform import sort_sha1
        return sort_sha1

    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')

