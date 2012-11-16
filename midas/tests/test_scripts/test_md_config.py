# -*- coding: utf-8 -*-

import tempfile

from midas.tests.test_scripts import IntegrationTestCaseNG

class MDConfigTests(IntegrationTestCaseNG):

    def _get_target_cls(self):
        from midas.scripts.md_config import MDConfig
        return MDConfig

    def test_without_arguments(self):
        self.assertEqual(self._call_cmd(), 0)
        self.assert_cls_out_startswith('[DEFAULT]\n')

    def test_with_job_cfg(self):
        with tempfile.NamedTemporaryFile('w+') as tmp:
            tmp.writelines('\n'.join(['[DEFAULT]',
                                      'user_name = foo']))
            tmp.seek(0)
            self.assertEqual(0, self._call_cmd(tmp.name))
        self.assert_cls_out_startswith('[DEFAULT]\n')
        self.assert_in_cls_out('user_name = foo')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
