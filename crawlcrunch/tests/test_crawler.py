# -*- coding: utf-8 -*-

import json
import os.path
import shutil
import tempfile
import threading

import mock

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import HTTPError
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import DummyCompany
from crawlcrunch.tests import DummyCompanyList
from crawlcrunch.tests import DummyRoot
from crawlcrunch.tests import prepare_url_open
from crawlcrunch.tests import unittest


class UpdaterTests(unittest.TestCase):

    def test_update_on_companies_list_is_called(self):
        from crawlcrunch.crawler import Updater
        root = mock.MagicMock()
        root.not_local.return_value = []
        updater = Updater(root)
        updater.run()
        root.update.assert_called_once_with()


class CompanyFetcherTests(unittest.TestCase):

    @mock.patch('logging.critical')
    def test_semaphore_is_released_on_error(self, critical):
        import logging
        logging.root.setLevel(logging.CRITICAL)
        semaphore = threading.Semaphore(1)
        dc = DummyCompany()
        dc.update().side_effect = Exception()

        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher(dc, semaphore)
        cf.run()
        self.assertTrue(semaphore.acquire(False))
        critical.assert_called_once()

    @mock.patch('logging.critical')
    def test_404_is_properly_handled(self, critical):

        class DummyCompany(object):

            name = 'foo'

            def update(self):
                raise HTTPError(None, 404, 'Not Found', None, None)

        semaphore = threading.Semaphore(1)
        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher(DummyCompany(), semaphore)
        cf.run()
        critical.assert_called_once_with("foo: Got 404")
        self.assertTrue(semaphore.acquire(False))

    @mock.patch('logging.exception')
    def test_not_404_is_logged(self, exc):
        class DummyCompany(object):
            name = 'foo'

            def update(self):
                raise HTTPError(None, 400, None, None, None)
        semaphore = threading.Semaphore(1)
        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher(DummyCompany(), semaphore)
        cf.run()
        exc.assert_called_once()
        self.assertTrue(semaphore.acquire(False))


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('crawlcrunch.compat.urlopen')
    def test_only_company_fetcher(self, urlopen):
        url = 'http://api.crunchbase.com/v/1/company/facebook.js'
        prepare_url_open(urlopen, {url: {'foo': 'bar'}, })
        dump_file = os.path.join(self.tmpd, 'facebook.json.gz')
        from crawlcrunch.crawler import CompanyFetcher
        from crawlcrunch.model.local_files import CompanyList
        cl = CompanyList(DummyRoot(), self.tmpd)
        cf = CompanyFetcher(cl.get('facebook'),
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(url)
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.load(fp), {'foo': 'bar'})

    def test_crawler_and_company_fetcher_play_together(self):
        cl = DummyCompanyList()
        cl.list_not_local.return_value = ['facebook', ]
        from crawlcrunch.crawler import Updater
        crawler = Updater(cl)
        crawler.run()
        fb = cl.get.assert_called_once_with('facebook')
        fb = cl.get('facebook')
        fb.update.assert_called_once_with()

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
