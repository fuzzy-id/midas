# -*- coding: utf-8 -*-

import datetime
import os
import os.path
import shutil
import sys
import tempfile

PY_VERSION = sys.version_info[:2]

if PY_VERSION == (2, 6):  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

from ev_transpose import Entry
from ev_transpose.compat import GzipFile
from ev_transpose.compat import StringIO


__here__ = os.path.abspath(os.path.dirname(__file__))
__test_data__ = os.path.join(__here__, 'data')
TEST_DATA = (
    (os.path.join(__test_data__, 'top-1m-2012-09-03.csv.zip', ),
     (Entry('foo', '2012-09-03', 1),
      Entry('bar', '2012-09-03', 2)),
     {'foo': [b'foo, 2012-09-03, 1', ],
      'bar': [b'bar, 2012-09-03, 2', ]}), )


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


class MainTests(PatchedStderrTestCase):

    def test_main_wo_arguments(self):
        from ev_transpose.script import main
        with self.assertRaises(SystemExit):
            main(['ev_transpose'])
        self.assert_err_endswith('too few arguments\n')


class EvTransposeTests(unittest.TestCase):

    def _make_one(self, *args):
        from ev_transpose.script import EvTranspose
        effargs = ['ev_transpose']
        effargs.extend(args)
        return EvTranspose(effargs)

    def test_expand_fname(self):
        et = self._make_one('/foo', None)
        self.assertEqual(et.expand('bar'), '/foo/bar.gz')

    def test_format_out(self):
        et = self._make_one(None, None)
        e = Entry(name='example.com', rank=2, 
                  date=datetime.datetime(1900, 1, 1))
        self.assertEqual(et.format_out(e), 
                         'example.com, 1900-01-01, 2')


class HelperTests(unittest.TestCase):

    def test_unzipping_file(self):
        from ev_transpose.script import unzip_file
        result = list(unzip_file(TEST_DATA[0][0]))
        expected = [ '{e.rank},{e.name}'.format(e=entry)
                     for entry in TEST_DATA[0][1] ]
        self.assertEqual(result, expected)

    def test_parse_line(self):
        from ev_transpose.script import split_rank_name
        result = split_rank_name('1,foo')
        self.assertEqual(result, (1, 'foo'))

    def test_parse_line_w_comma_in_name(self):
        ' This seems to happen. *sigh* '
        from ev_transpose.script import split_rank_name
        result = split_rank_name('1,foo,bar')
        self.assertEqual(result, (1, 'foo,bar'))


class IntegrationTests(PatchedStderrTestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _test_it(self, *args):
        from ev_transpose.script import main
        effargs = ['ev_transpose']
        effargs.extend(args)
        return main(effargs)

    def test_on_test_data_one(self):
        cmd = self._test_it(self.tmpd, TEST_DATA[0][0])
        self.assertEqual(cmd, 0)
        dir_listing = os.listdir(self.tmpd)
        dir_listing.sort()
        self.assertEqual(dir_listing, ['bar.gz', 'foo.gz'])
        with GzipFile(os.path.join(self.tmpd, 'bar.gz')) as fp:
            self.assertEqual(fp.readlines(), TEST_DATA[0][2]['bar'])
        with GzipFile(os.path.join(self.tmpd, 'foo.gz')) as fp:
            self.assertEqual(fp.readlines(), TEST_DATA[0][2]['foo'])
