# -*- coding: utf-8 -*-

import sys

from ev_transpose.compat import StringIO
from ev_transpose.tests import unittest

class ArgParserTests(unittest.TestCase):

    def setUp(self):
        self._olderr = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self._olderr

    def _make_one(self, *args):
        from ev_transpose.script import EvTranspose
        effargs = ['ev_transpose']
        effargs.extend(args)
        return EvTranspose(effargs).args

    def test_no_arguments_raises_error(self):
        with self.assertRaises(SystemExit):
            self._make_one()
        sys.stderr.seek(0)
        err = sys.stderr.getvalue()
        self.assertTrue(err.endswith('too few arguments\n'))

    def test_only_one_argument_raises_error(self):
        with self.assertRaises(SystemExit):
            self._make_one('foo')
        sys.stderr.seek(0)
        err = sys.stderr.getvalue()
        self.assertTrue(err.endswith('too few arguments\n'))

    def test_one_dst_and_one_file(self):
        args = self._make_one('foo', 'bar')
        self.assertEqual(args.dst, 'foo')
        self.assertEqual(args.zip_file, ['bar', ])
    
    def test_one_dst_and_several_files(self):
        args = self._make_one('foo', 'bar', 'baz')
        self.assertEqual(args.dst, 'foo')
        self.assertEqual(args.zip_file, ['bar', 'baz'])
