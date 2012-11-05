# -*- coding: utf-8 -*-

from midas.tests.test_scripts import IntegrationTestCase

class AlexaZipToGzipTests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.alexa_zip_to_gzip import AlexaZipToGzip
        return AlexaZipToGzip.cmd

    def test_help_flag(self):
        with self.assertRaises(SystemExit) as cm:
            self._run_it('-h')
        self.assertEqual(cm.exception.code, 0)
        self.assert_stdout_startswith('usage: ')
