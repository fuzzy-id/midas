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
from midas.tests import FOO_URL
from midas.tests import DummyCompany
from midas.tests import DummyCompanyList
from midas.tests import prepare_url_open
from midas.tests.test_scripts import IntegrationTestCase

import mock


class FetcherBehaviourOnErrorTests(unittest.TestCase):

    def _test_it(self, company):
        from midas.scripts.fetch_crunchbase_companies import Fetcher
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
        self.assertEqual(critical.call_count, 1)

    @mock.patch('logging.critical')
    def test_404_is_properly_handled(self, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 404, 'Not Found', None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        self.assertEqual(critical.call_count, 1)

    @mock.patch('logging.exception')
    def test_not_400_is_logged(self, exc):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 400, None, None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        self.assertEqual(dc.update.call_count, 1)
        self.assertEqual(exc.call_count, 1)

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_504_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 504, None, None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        self.assertEqual(dc.update.call_count, 3)
        self.assertEqual(critical.call_count, 2)
        self.assertEqual(exc.call_count, 1)

    @mock.patch('logging.critical')
    @mock.patch('logging.exception')
    def test_503_is_logged_but_retry_happens(self, exc, critical):
        dc = DummyCompany()
        dc.update.side_effect = HTTPError(None, 503, None, None, None)
        q = self._test_it(dc)
        q.join()
        self.assertTrue(q.empty())
        self.assertEqual(dc.update.call_count, 3)
        self.assertEqual(critical.call_count, 2)
        self.assertEqual(exc.call_count, 1)


class MainLocalFilesIntegrationTests(IntegrationTestCase):

    def _get_target_cls(self):
        from midas.scripts.fetch_crunchbase_companies import FetchCrunchbaseCompanies
        return FetchCrunchbaseCompanies

    @mock.patch('midas.crunchbase_company.urlopen')
    def test_on_empty_companies_list(self, urlopen):
        url_return = {COMPANIES_URL: []}
        prepare_url_open(urlopen, url_return)
        self.assertEqual(self._call_cmd(self.tmpd), 0)
        urlopen.assert_called_once_with(COMPANIES_URL)
        self.assertEqual(os.listdir(self.tmpd), [])

    @mock.patch('midas.crunchbase_company.urlopen')
    def test_on_companies_list_with_elements(self, urlopen):
        prepare_url_open(urlopen,
                         {COMPANIES_URL: [{'permalink': 'foo', },
                                          {'permalink': 'bar', }],
                          FOO_URL: ['some_foo'],
                          BAR_URL: ['some_bar']})
        self.assertEqual(self._call_cmd('-q', self.tmpd), 0)
        try:
            urlopen.assert_called_with(BAR_URL)
        except AssertionError:  # pragma: no cover
            urlopen.assert_called_with(FOO_URL)
        listing = os.listdir(self.tmpd)
        listing.sort()
        self.assertEqual(listing, ['bar.json',
                                   'foo.json'])
        with open(os.path.join(self.tmpd, 'bar.json')) as fp:
            self.assertEqual(json.loads(fp.read().decode()),
                             ['some_bar', ])
        with open(os.path.join(self.tmpd, 'foo.json')) as fp:
            self.assertEqual(json.loads(fp.read().decode()), 
                             ['some_foo', ])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
