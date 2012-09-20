# -*- coding: utf-8 -*-

import sys

import mock

from midas.compat import StringIO
from midas.tests import IntegrationTestCase

class AlexaToSha1Tests(IntegrationTestCase):

    def _run(self, *args):
        effargs = ['md_alexa_to_sha1']
        effargs.extend(args)
        from midas.transform import alexa_to_sha1
        return alexa_to_sha1(effargs)
        
    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')
