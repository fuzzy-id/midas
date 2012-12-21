# -*- coding: utf-8 -*-

import json
import logging
import os
import os.path
import shutil
import sys
import tempfile

from midas.compat import GzipFile
from midas.compat import StringIO
from midas.compat import unittest

from midas.tests.test_crunchbase_crawler import BAR_URL
from midas.tests.test_crunchbase_crawler import COMPANIES_URL
from midas.tests.test_crunchbase_crawler import EXAMPLES_PATH
from midas.tests.test_crunchbase_crawler import FOO_URL
from midas.tests.test_crunchbase_crawler import prepare_url_open

import mock


class ArgumentParserTests(unittest.TestCase):

    def setUp(self):
        self._old_err = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self._old_err

    def _make_one(self, *args):
        from midas.scripts.cc_update import CCUpdateCommand
        effargs = ['crawlcrunch', ]
        effargs.extend(args)
        return CCUpdateCommand(effargs)

    def test_defaults(self):
        cmd = self._make_one('.')
        self.assertEqual(cmd.args.location, '.')
        self.assertEqual(cmd.args.classes, ['companies'])

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
        from midas.scripts.cc_update import main
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


class MainIntegrationTestCase(unittest.TestCase):

    def _test_it(self, *args):
        from midas.scripts.cc_update import main
        effargs = ['cc_update', '-qqq']
        effargs.extend(args)
        return main(effargs)


class MainLocalFilesIntegrationTests(MainIntegrationTestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_on_empty_companies_list(self, urlopen):
        url_return = {COMPANIES_URL: []}
        prepare_url_open(urlopen, url_return)
        self.assertEqual(self._test_it(self.tmpd), 0)
        urlopen.assert_called_once_with(COMPANIES_URL)
        self.assertEqual(os.listdir(self.tmpd), [])

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_on_companies_list_with_elements(self, urlopen):
        prepare_url_open(urlopen,
                         {COMPANIES_URL: [{'permalink': 'foo', },
                                          {'permalink': 'bar', }],
                          FOO_URL: ['some_foo'],
                          BAR_URL: ['some_bar']})
        self.assertEqual(self._test_it(self.tmpd), 0)
        try:
            urlopen.assert_called_with(BAR_URL)
        except AssertionError:  # pragma: no cover
            urlopen.assert_called_with(FOO_URL)
        listing = os.listdir(self.tmpd)
        listing.sort()
        self.assertEqual(listing, ['bar.json.gz',
                                   'foo.json.gz'])
        with GzipFile(os.path.join(self.tmpd,
                                   'bar.json.gz')) as fp:
            self.assertEqual(json.loads(fp.read().decode()),
                             ['some_bar', ])
        with GzipFile(os.path.join(self.tmpd,
                                   'foo.json.gz')) as fp:
            self.assertEqual(json.loads(fp.read().decode()), 
                             ['some_foo', ])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
