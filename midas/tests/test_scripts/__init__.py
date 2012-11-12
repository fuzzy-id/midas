# -*- coding: utf-8 -*-

import sys

from vincetools.compat import StringIO
from vincetools.compat import unittest

import vincetools.compat as vt_comp

import midas.tests as md_tests

class IntegrationTestCase(unittest.TestCase):

    def _run_it(self, *args):
        effargs = ['script_name']
        effargs.extend(args)
        return self._get_target_func()(effargs)
        
    def setUp(self):
        import midas.config as md_cfg
        md_cfg.set('hadoop', 'exec', 'echo')
        self._oldout = sys.stdout
        sys.stdout = StringIO()
        self._oldin = sys.stdin
        sys.stdin = StringIO()

    def tearDown(self):
        import midas.config as md_cfg
        md_cfg.new_configparser()
        sys.stdout = self._oldout
        sys.stdin = self._oldin

    def _get_stdout(self):
        sys.stdout.seek(0)
        return sys.stdout.getvalue()

    def assert_stdout_startswith(self, s):
        out = self._get_stdout()
        self.assertTrue(out.startswith(s), 
                        '"{0!r}" does not start with {1!r}'.format(out, s))

    def assert_stdout_equal(self, s):
        out = self._get_stdout()
        self.assertEqual(out, s)

    def assert_in_stdout(self, s):
        out = self._get_stdout()
        self.assertIn(s, out)


class IntegrationTestCaseNG(md_tests.ConfiguredDBTestCase):

    def setUp(self):
        md_tests.ConfiguredDBTestCase.setUp(self)
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
