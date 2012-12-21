# -*- coding: utf-8 -*-

import sys

from midas.compat import StringIO
from midas.compat import unittest

import midas.compat as vt_comp

import midas.tests as md_tests
import midas.config as md_cfg

class IntegrationTestCaseNG(unittest.TestCase):

    def setUp(self):
        md_cfg.set('location', 'data_home', md_tests._test_data_home)
        self.out = vt_comp.StringIO()

    def _call_cmd(self, *args):
        cls = self._get_target_cls()
        cls._out = self.out
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
