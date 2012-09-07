# -*- coding: utf-8 -*-

import os
import shutil
import sys
import tempfile

from ev_transpose.compat import StringIO
from ev_transpose.tests import TEST_DATA 
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

    def assert_err_endswith(self, s):
        err = self._get_err_msg()
        self.assertTrue(err.endswith(s))

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
        self.assert_err_endswith('too few arguments\n')

    def test_only_one_argument_raises_error(self):
        with self.assertRaises(SystemExit):
            self._make_one('foo')
        err = self._get_err_msg()
        self.assert_err_endswith('too few arguments\n')

    def test_one_dst_and_one_file(self):
        args = self._make_one('foo', 'bar')
        self.assertEqual(args.dst, 'foo')
        self.assertEqual(args.zip_file, ['bar', ])
    
    def test_one_dst_and_several_files(self):
        args = self._make_one('foo', 'bar', 'baz')
        self.assertEqual(args.dst, 'foo')
        self.assertEqual(args.zip_file, ['bar', 'baz'])

class EvTransposeTests(PatchedStderrTestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_one(self, *args):
        from ev_transpose.script import EvTranspose
        effargs = ['ev_transpose']
        effargs.extend(args)
        return EvTranspose(effargs)

    def test_on_test_data_one(self):
        cmd = self._make_one(self.tmpd, *TEST_DATA[0][0])
        self.assertEqual(cmd.run(), 0)
        dir_listing = os.listdir(self.tmpd)
        dir_listing.sort()
        self.assertEqual(dir_listing, ['bar.gz', 'foo.gz'])
        with GzipFile(os.path.join(self.tmpd, 'bar.gz')) as fp:
            self.assertEqual(fp.readlines(), TEST_DATA[0][1]['bar'])
        with GzipFile(os.path.join(self.tmpd, 'foo.gz')) as fp:
            self.assertEqual(fp.readlines(), TEST_DATA[0][1]['foo'])

class IntegrationTests(PatchedStderrTestCase):

    def test_main_wo_arguments(self):
        from ev_transpose.script import main
        with self.assertRaises(SystemExit):
            main(['ev_transpose'])
        self.assert_err_endswith('too few arguments\n')
