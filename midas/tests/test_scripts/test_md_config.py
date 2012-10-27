# -*- coding: utf-8 -*-

import tempfile

import vincetools.compat as vt_comp

from midas.tests.test_scripts import IntegrationTestCase

class MDConfigTests(IntegrationTestCase):

    def _get_target_func(self):
        from midas.scripts.md_config import MDConfig
        return MDConfig.cmd

    def test_without_arguments(self):
        self.assertEqual(self._run_it(), 0)
        self.assert_stdout_startswith('[DEFAULT]\n')

    def test_with_job_cfg(self):
        with tempfile.NamedTemporaryFile('w+') as tmp:
            tmp.writelines('\n'.join(['[DEFAULT]',
                                      'user_name = foo']))
            tmp.seek(0)
            self.assertEqual(0, self._run_it(tmp.name))
        self.assert_stdout_startswith('[DEFAULT]\n')
        self.assert_in_stdout('user_name = foo')

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
