# -*- coding: utf-8 -*-

import shutil
import tempfile

from midas.compat import StringIO
from midas.compat import unittest

class MDCommandTestCase(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
        self.stdin = StringIO()

    def prepare_stdout(self, cls):
        cls._out = self.out

    def prepare_stdin(self, cls):
        self.stdin.seek(0)
        cls._in = self.stdin

    def _get_and_initialize_cls(self):
        cls = self._get_target_cls()
        self.prepare_stdout(cls)
        self.prepare_stdin(cls)
        return cls

    def _make_effargs(self, *args):
        effargs = ["md_command"]
        effargs.extend(args)
        return effargs

    def make_object(self, *args):
        cls = self._get_and_initialize_cls()
        effargs = self._make_effargs(*args)
        return cls(effargs)

    def _call_cmd(self, *args):
        cls = self._get_and_initialize_cls()
        effargs = self._make_effargs(*args)
        return cls.cmd(effargs)

    def _get_value(self, buf):
        buf.seek(0)
        return buf.getvalue()

    def assert_call_succeeds(self, *args):
        ret_val = self._call_cmd(*args)
        self.assertEqual(ret_val, 0)

    def assert_in_cls_out(self, s):
        out = self._get_value(self.out)
        self.assertIn(s, out)

    def assert_stdout_equal(self, s):
        out = self._get_value(self.out)
        self.assertEqual(out, s)


class IntegrationTestCase(MDCommandTestCase):

    def setUp(self):
        MDCommandTestCase.setUp(self)
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)
