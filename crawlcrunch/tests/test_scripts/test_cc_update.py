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
from crawlcrunch.tests import MEM_DB
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest

import mock


COMPANIES_URL = 'http://api.crunchbase.com/v/1/companies.js'

class ArgumentParserTests(unittest.TestCase):

    def setUp(self):
        self._old_err = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self._old_err

    def _make_one(self, *args):
        from crawlcrunch.scripts.cc_update import CCUpdateCommand
        effargs = ['crawlcrunch', ]
        effargs.extend(args)
        return CCUpdateCommand(effargs)

    def test_defaults(self):
        cmd = self._make_one('.')
        self.assertEqual(cmd.args.location, '.')
        self.assertEqual(cmd.args.classes, ['companies'])
        self.assertFalse(cmd.args.sql)

    def test_missing_argument(self):
        with self.assertRaises(SystemExit):
            self._make_one()

    def test_non_existent_path(self):
        dst = os.path.join('non', 'existent', 'path', )
        with self.assertRaises(SystemExit) as cm:
            self._make_one(dst)
        e = cm.exception
        self.assertEqual(e.code, 2)
        err = sys.stderr.getvalue()
        self.assertTrue(err.endswith(
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

    def _test_it(self, *args):
        from crawlcrunch.scripts.cc_update import main
        effargs = ['cc_update']
        effargs.extend(args)
        return main(effargs)

    def test_missing_argument(self):
        with self.assertRaises(SystemExit) as cm:
            self._test_it()
        self.assertEqual(cm.exception.code, 2)
        err = sys.stderr.getvalue()
        self.assertTrue(err.endswith('too few arguments\n'))

    def test_with_wrong_class(self):
        with self.assertRaises(ValueError) as cm:
            self._test_it('-qqq', '.', 'no_such_class')
        e = cm.exception
        self.assertEqual(len(e.args), 1)
        self.assertTrue(e.args[0].endswith("'no_such_class'"))

    def test_with_wrong_class_on_sql(self):
        with self.assertRaises(ValueError) as cm:
            self._test_it('-qqq', '--sql', MEM_DB, 'no_such_class')
        e = cm.exception
        self.assertEqual(len(e.args), 1)
        self.assertTrue(e.args[0].endswith("'no_such_class'"))


class MainIntegrationTestCase(unittest.TestCase):

    def _test_it(self, *args):
        from crawlcrunch.scripts.cc_update import main
        effargs = ['cc_update', '-qqq']
        effargs.extend(args)
        return main(effargs)


class MainLocalFilesIntegrationTests(MainIntegrationTestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_on_empty_companies_list(self, urlopen):
        url_return = {COMPANIES_URL: []}
        prepare_url_open(urlopen, url_return)
        self.assertEqual(self._test_it(self.tmpd), 0)
        urlopen.assert_called_once_with(COMPANIES_URL)
        self.assertEqual(os.listdir(self.tmpd), [])

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_on_companies_list_with_elements(self, urlopen):
        foo_url = 'http://api.crunchbase.com/v/1/company/foo.js'
        bar_url = 'http://api.crunchbase.com/v/1/company/bar.js'
        prepare_url_open(urlopen,
                         {COMPANIES_URL: [{'permalink': 'foo', },
                                          {'permalink': 'bar', }],
                          foo_url: ['some_foo'],
                          bar_url: ['some_bar']})
        self.assertEqual(self._test_it(self.tmpd), 0)
        urlopen.assert_called_with(bar_url)
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


class MainSqlIntegrationTests(MainIntegrationTestCase):

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_on_empty_companies_list(self, urlopen):
        url_return = {COMPANIES_URL: []}
        prepare_url_open(urlopen, url_return)
        self.assertEqual(self._test_it('--sql', MEM_DB), 0)
        urlopen.assert_called_once_with(COMPANIES_URL)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
