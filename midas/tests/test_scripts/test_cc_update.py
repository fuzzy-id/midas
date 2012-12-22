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
from midas.tests.test_scripts import IntegrationTestCaseNG

import mock


class FetcherBehaviourOnErrorTests(unittest.TestCase):

    def _test_it(self, company):
        from midas.scripts.cc_update import Fetcher
        from midas.compat import Queue
        q = Queue()
        q.put(company)
        cf = Fetcher(q)
        cf.daemon = True
        cf.start()
        return q

    @mock.patch('logging.critical')
    def test_task_is_done_on_error(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = Exception()
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        critical.assert_called_once()

    @mock.patch('logging.critical')
    def test_404_is_properly_handled(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 404, 'Not Found', None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        critical.assert_has_calls([])
        critical.assert_called_once()

    @mock.patch('logging.exception')
    def test_not_404_is_logged(self, exc):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 400, None, None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        dc.update.assert_called_once()
        exc.assert_called_once()

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_504_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 504, None, None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        dc.update.assert_called_once()
        exc.assert_called_once()
        self.assertEqual(critical.call_count, 2)

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_503_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 503, None, None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        dc.update.assert_called_once()
        exc.assert_called_once()
        self.assertEqual(critical.call_count, 2)


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


class MainLocalFilesIntegrationTests(IntegrationTestCaseNG):

    def _get_target_cls(self):
        from midas.scripts.cc_update import CCUpdateCommand
        return CCUpdateCommand

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_on_empty_companies_list(self, urlopen):
        url_return = {COMPANIES_URL: []}
        prepare_url_open(urlopen, url_return)
        self.assertEqual(self._call_cmd(self.tmpd), 0)
        urlopen.assert_called_once_with(COMPANIES_URL)
        self.assertEqual(os.listdir(self.tmpd), [])

    @mock.patch('midas.crunchbase_crawler.urlopen')
    def test_on_companies_list_with_elements(self, urlopen):
        prepare_url_open(urlopen,
                         {COMPANIES_URL: [{'permalink': 'foo', },
                                          {'permalink': 'bar', }],
                          FOO_URL: ['some_foo'],
                          BAR_URL: ['some_bar']})
        self.assertEqual(self._call_cmd(self.tmpd), 0)
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
