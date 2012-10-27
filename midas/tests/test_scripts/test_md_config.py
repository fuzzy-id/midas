# -*- coding: utf-8 -*-

from midas.tests.test_scripts import IntegrationTestCase

class MDConfigTests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.md_config import MDConfig
        return MDConfig.cmd

    def test_without_arguments(self):
        self.assertEqual(self._run_it(), 0)
        self.assert_stdout_startswith('[DEFAULT]\n')
