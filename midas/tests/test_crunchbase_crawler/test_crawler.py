# -*- coding: utf-8 -*-

import json
import os.path
import shutil
import tempfile
import threading

import mock

from midas.compat import GzipFile
from midas.compat import HTTPError
from midas.compat import StringIO

from midas.tests.test_crunchbase_crawler import FOO_URL
from midas.tests.test_crunchbase_crawler import DummyCompany
from midas.tests.test_crunchbase_crawler import DummyCompanyList
from midas.tests.test_crunchbase_crawler import DummyRoot
from midas.tests.test_crunchbase_crawler import prepare_url_open
from midas.tests.test_crunchbase_crawler import unittest


class UpdaterTests(unittest.TestCase):

    def test_update_on_companies_list_is_called(self):
        from midas.crunchbase_crawler.crawler import Updater
        dcl = DummyCompanyList()
        dcl.list_not_local.return_value = []
        updater = Updater(dcl)
        updater.run()
        dcl.update.assert_called_once_with()


class FetcherTests(unittest.TestCase):

    def _test_it(self, company):
        from midas.crunchbase_crawler.crawler import Fetcher
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

    @mock.patch('midas.crunchbase_crawler.model.urlopen')
    def test_company_fetcher_and_company_list(self, urlopen):
        from midas.crunchbase_crawler.crawler import Fetcher
        from midas.crunchbase_crawler.model.local_files import CompanyList
        prepare_url_open(urlopen, {FOO_URL: {'foo': 'bar'}, })
        dump_file = os.path.join(self.tmpd, 'foo.json.gz')
        cl = CompanyList(DummyRoot(), self.tmpd)
        cf = Fetcher(cl.get('foo'),
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(FOO_URL)
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.loads(fp.read().decode()), {'foo': 'bar'})

    def test_crawler_and_company_fetcher_play_together(self):
        from midas.crunchbase_crawler.crawler import Updater
        cl = DummyCompanyList()
        cl.list_not_local.return_value = (cl.get('facebook'), )
        crawler = Updater(cl)
        crawler.run()
        fb = cl.get.assert_called_once_with('facebook')
        fb = cl.get('facebook')
        fb.update.assert_called_once_with()

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
