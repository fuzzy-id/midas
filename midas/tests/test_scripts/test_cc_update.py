# -*- coding: utf-8 -*-

import json
import logging
import os
import os.path
import shutil
import sys
import tempfile
import threading

from midas.compat import GzipFile
from midas.compat import HTTPError
from midas.compat import StringIO
from midas.compat import unittest

from midas.tests import BAR_URL
from midas.tests import COMPANIES_URL
from midas.tests import EXAMPLES_PATH
from midas.tests import FOO_URL
from midas.tests import DummyCompany
from midas.tests import DummyCompanyList
from midas.tests import prepare_url_open

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


class UpdaterTests(unittest.TestCase):

    def test_update_on_companies_list_is_called(self):
        from midas.scripts.cc_update import Updater
        dcl = DummyCompanyList()
        dcl.list_not_local.return_value = []
        updater = Updater(dcl)
        updater.run()
        dcl.update.assert_called_once_with()


class FetcherBehaviourOnErrorTests(unittest.TestCase):

    def _test_it(self, company):
        from midas.scripts.cc_update import Fetcher
        semaphore = mock.MagicMock()
        cf = Fetcher(company, semaphore)
        cf.run()
        return cf, semaphore

    @mock.patch('logging.critical')
    def test_semaphore_is_released_on_error(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = Exception()
        _, semaphore = self._test_it(dc)
        semaphore.release.assert_called_once_with()
        critical.assert_called_once()

    @mock.patch('logging.critical')
    def test_404_is_properly_handled(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 404, 'Not Found', None, None)
        _, semaphore = self._test_it(dc)
        critical.assert_has_calls([])
        critical.assert_called_once()
        semaphore.release.assert_called_once_with()

    @mock.patch('logging.exception')
    def test_not_404_is_logged(self, exc):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 400, None, None, None)
        _, semaphore = self._test_it(dc)
        dc.update.assert_called_once()
        exc.assert_called_once()
        semaphore.release.assert_called_once_with()

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_504_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 504, None, None, None)
        _, semaphore = self._test_it(dc)
        dc.update.assert_called_once()
        exc.assert_called_once()
        self.assertEqual(critical.call_count, 2)
        self.assertEqual(semaphore.release.call_count, 3)

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_503_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 503, None, None, None)
        _, semaphore = self._test_it(dc)
        dc.update.assert_called_once()
        exc.assert_called_once()
        self.assertEqual(critical.call_count, 2)
        self.assertEqual(semaphore.release.call_count, 3)


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_company_fetcher_and_company_list(self, urlopen):
        from midas.scripts.cc_update import Fetcher
        from midas.crunchbase_crawler import CompanyList
        prepare_url_open(urlopen, {FOO_URL: {'foo': 'bar'}, })
        dump_file = os.path.join(self.tmpd, 'foo.json.gz')
        cl = CompanyList(self.tmpd)
        cf = Fetcher(cl.get('foo'),
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(FOO_URL)
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.loads(fp.read().decode()), {'foo': 'bar'})

    def test_crawler_and_company_fetcher_play_together(self):
        from midas.scripts.cc_update import Updater
        cl = DummyCompanyList()
        cl.list_not_local.return_value = (cl.get('facebook'), )
        crawler = Updater(cl)
        crawler.run()
        fb = cl.get.assert_called_once_with('facebook')
        fb = cl.get('facebook')
        fb.update.assert_called_once_with()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
