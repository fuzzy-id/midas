# -*- coding: utf-8 -*-

from midas.compat import StringIO
from midas.compat import unittest


class IntegrationTestCaseNG(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()

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
