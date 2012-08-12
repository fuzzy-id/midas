# -*- coding: utf-8 -*-

import json
import os.path
import shutil
import tempfile
import threading

import mock

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import unittest

class CompanyFetcherTests(unittest.TestCase):

    def test_semaphore_is_released_on_error(self):
        import logging
        logging.root.setLevel(logging.CRITICAL)
        semaphore = threading.Semaphore(1)
        class DummyCompany(object):
            def update(self):
                raise Exception()
        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher(DummyCompany(), semaphore)
        cf.run()
        self.assertTrue(semaphore.acquire(False))

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('crawlcrunch.model.url_open')
    def test_only_company_fetcher(self, urlopen):
        content = StringIO()
        json.dump({'foo': 'bar'}, content)
        content.seek(0)
        urlopen.return_value = content
        dump_file = os.path.join(self.tmpd, 'facebook.json.gz')
        from crawlcrunch.crawler import CompanyFetcher
        from crawlcrunch.model import LocalFilesDir
        root = LocalFilesDir(self.tmpd)
        cf = CompanyFetcher(root.get('facebook'),
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(
            'http://api.crunchbase.com/v/1/company/facebook.js'
            )
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.load(fp), {'foo': 'bar'})

    @mock.patch('crawlcrunch.model.url_open')
    def test_crawler_and_company_fetcher(self, urlopen):
        content = StringIO()
        json.dump({'foo': 'bar'}, content)
        content.seek(0)
        urlopen.return_value = content
        from crawlcrunch.crawler import Crawler
        from crawlcrunch.model import LocalFilesDir
        root = LocalFilesDir(self.tmpd)
        cl = root.get('companies')
        cl.data.append('facebook')
        crawler = Crawler(root)
        crawler.crawl()
        urlopen.assert_called_once_with(
            'http://api.crunchbase.com/v/1/company/facebook.js'
            )
        with GzipFile(os.path.join(self.tmpd, 'facebook.json.gz')) as fp:
            self.assertEqual(json.load(fp), {'foo': 'bar'})

if __name__ == '__main__': # pragma: no cover
    unittest.main()
