# -*- coding: utf-8 -*-

import sys

from ev_transpose.compat import StringIO
from ev_transpose.tests import unittest

class PatchedStderrTestCase(unittest.TestCase):

    def setUp(self):
        self._olderr = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self._olderr

    def _get_err_msg(self):
        sys.stderr.seek(0)
        return sys.stderr.getvalue()

class ArgParserTests(PatchedStderrTestCase):

    def _make_one(self, *args):
        from ev_transpose.script import EvTranspose
        effargs = ['ev_transpose']
        effargs.extend(args)
        return EvTranspose(effargs).args

    def test_no_arguments_raises_error(self):
        with self.assertRaises(SystemExit):
            self._make_one()
        err = self._get_err_msg()
        self.assertTrue(err.endswith('too few arguments\n'))

    def test_only_one_argument_raises_error(self):
        with self.assertRaises(SystemExit):
            self._make_one('foo')
        err = self._get_err_msg()
        self.assertTrue(err.endswith('too few arguments\n'))

    def test_one_dst_and_one_file(self):
        args = self._make_one('foo', 'bar')
        self.assertEqual(args.dst, 'foo')
        self.assertEqual(args.zip_file, ['bar', ])
    
    def test_one_dst_and_several_files(self):
        args = self._make_one('foo', 'bar', 'baz')
        self.assertEqual(args.dst, 'foo')
        self.assertEqual(args.zip_file, ['bar', 'baz'])

class IntegrationTests(PatchedStderrTestCase):

    def test_main_wo_arguments(self):
        from ev_transpose.script import main
        with self.assertRaises(SystemExit):
            main(['ev_transpose'])
        err = self._get_err_msg()
        self.assertTrue(err.endswith('too few arguments\n'))
