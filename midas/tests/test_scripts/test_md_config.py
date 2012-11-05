# -*- coding: utf-8 -*-

import tempfile

import vincetools.compat as vt_comp

from midas.tests.test_scripts import IntegrationTestCase

class IntegrationTestCaseNG(vt_comp.unittest.TestCase):

    def setUp(self):
        import midas.config as md_cfg
        md_cfg.new_configparser()
        self.out = vt_comp.StringIO()

    def _call_cmd(self, *args):
        cls = self._get_target_cls()
        cls.out = self.out
        effargs = [cls.__name__]
        effargs.extend(args)
        return cls.cmd(effargs)

    def _get_value(self, buf):
        buf.seek(0)
        return buf.getvalue()

    def assert_cls_out_startswith(self, s):
        out = self._get_value(self.out)
        self.assertTrue(out.startswith(s), 
                        '"{0!r}" does not start with {1!r}'.format(out, s))

    def assert_in_cls_out(self, s):
        out = self._get_value(self.out)
        self.assertIn(s, out)


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

    def test_check_cfg(self):
        pass

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
