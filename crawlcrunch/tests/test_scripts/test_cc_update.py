# -*- coding: utf-8 -*-

import json
import logging
import os
import os.path
import shutil
import sys
import tempfile

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import EXAMPLES_PATH
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest

import mock


class ArgumentParserTests(unittest.TestCase):

    def setUp(self):
        self._old_err = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self._old_err

    def _get_target_class(self):
        from crawlcrunch.scripts.cc_update import CCUpdateCommand
        return CCUpdateCommand

    def _make_one(self, *args):
        effargs = ['crawlcrunch', ]
        effargs.extend(args)
        return self._get_target_class()(effargs)

    def test_defaults(self):
        cmd = self._make_one('.')
        self.assertEqual(cmd.args.location, '.')
        self.assertEqual(cmd.args.classes, ['companies'])
        self.assertFalse(cmd.args.sql)

    def test_missing_argument(self):
        with self.assertRaises(SystemExit):
            self._make_one()

    def test_too_much_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            cmd = self._make_one('one', 'two', )
        e = cm.exception
        self.assertEqual(e.code, 2)

    def test_non_existent_path(self):
        dst = os.path.join('non', 'existent', 'path', )
        with self.assertRaises(SystemExit) as cm:
            self._make_one(dst)
        e = cm.exception
        self.assertEqual(e.code, 2)
        err = sys.stderr.getvalue()
        self.assertTrue(
            err.endswith(
                "the directory 'non/existent/path' does not exist\n"\
                    .format(dst)))

    def test_verboseness_quietness_flags(self):
        cmd = self._make_one('-v', EXAMPLES_PATH['company_files_empty'])
        self.assertEqual(cmd.args.verbosity, logging.getLevelName('DEBUG'))
        cmd = self._make_one(EXAMPLES_PATH['company_files_empty'])
        self.assertEqual(cmd.args.verbosity, logging.getLevelName('INFO'))
        cmd = self._make_one('-q', EXAMPLES_PATH['company_files_empty'])
        self.assertEqual(cmd.args.verbosity, logging.getLevelName('WARNING'))
        cmd = self._make_one('-qq', EXAMPLES_PATH['company_files_empty'])
        self.assertEqual(cmd.args.verbosity, logging.getLevelName('ERROR'))
        cmd = self._make_one('-qqq', EXAMPLES_PATH['company_files_empty'])
        self.assertEqual(cmd.args.verbosity, logging.getLevelName('CRITICAL'))
        cmd = self._make_one('-qqvq', EXAMPLES_PATH['company_files_empty'])
        self.assertEqual(cmd.args.verbosity, logging.getLevelName('ERROR'))

    def test_passing_in_db_uri(self):
        cmd = self._make_one('--sql', 'sqlite:///:memory:')
        self.assertEqual(cmd.args.location, 'sqlite:///:memory:')

    def test_classes_flag(self):
        cmd = self._make_one('.', 'foo', 'bar')
        self.assertEqual(cmd.args.classes, ['foo', 'bar'])

class MainTests(unittest.TestCase):

    def setUp(self):
        self._old_err = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self._old_err

    def test_missing_argument(self):
        from crawlcrunch.scripts.cc_update import main
        with self.assertRaises(SystemExit) as cm:
            main(['cc_update'])
        self.assertEqual(cm.exception.code, 2)
        err = sys.stderr.getvalue()
        self.assertTrue(err.endswith('too few arguments\n'))


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    def _make_one(self, path):
        from crawlcrunch.scripts.cc_update import CCUpdateCommand
        return CCUpdateCommand(['cc_update', path])

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_on_empty_companies_list(self, url_open):
        url_return = (
            {'http://api.crunchbase.com/v/1/companies.js': []})
        prepare_url_open(url_open, url_return)
        from crawlcrunch.scripts.cc_update import main
        result = main(['cc_update', '-qqq', self.tmpd])
        self.assertEqual(result, 0)
        url_open.assert_called_once_with(
            'http://api.crunchbase.com/v/1/companies.js')
        listing = os.listdir(self.tmpd)
        self.assertEqual(listing, [])

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_on_companies_list_with_elements(self, url_open):
        companies_url = 'http://api.crunchbase.com/v/1/companies.js'
        foo_url = 'http://api.crunchbase.com/v/1/company/foo.js'
        bar_url = 'http://api.crunchbase.com/v/1/company/bar.js'
        prepare_url_open(url_open,
                         {companies_url: [{'permalink': 'foo', },
                                          {'permalink': 'bar', }],
                          foo_url: ['some_foo'],
                          bar_url: ['some_bar']})
        cmd = self._make_one(self.tmpd)
        result = cmd.run()
        self.assertEqual(result, 0)
        url_open.assert_called_with(bar_url)
        listing = os.listdir(self.tmpd)
        listing.sort()
        self.assertEqual(listing, ['bar.json.gz',
                                   'foo.json.gz'])

        with GzipFile(os.path.join(self.tmpd,
                                   'bar.json.gz')) as fp:
            self.assertEqual(json.load(fp), ['some_bar', ])
        with GzipFile(os.path.join(self.tmpd,
                                   'foo.json.gz')) as fp:
            self.assertEqual(json.load(fp), ['some_foo', ])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
