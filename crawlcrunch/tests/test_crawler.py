# -*- coding: utf-8 -*-

import json
import os.path
import shutil
import tempfile
import threading

import mock

from crawlcrunch import LocalFilesDir
from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import StringIO
from crawlcrunch.tests import unittest

class CompanyFetcherTests(unittest.TestCase):

    def _get_target_class(self):
        from crawlcrunch.crawler import CompanyFetcher
        return CompanyFetcher

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_url_generation(self):
        cf = self._make_one('facebook', 'dst', threading.Semaphore(1))
        expected = 'http://api.crunchbase.com/v/1/company/facebook.js'
        self.assertEqual(cf.query_url(), expected)

    @mock.patch('crawlcrunch.url_open')
    def test_semaphore_is_released_on_error(self, urlopen):
        urlopen.side_effect = Exception
        import logging
        logging.root.setLevel(logging.CRITICAL)
        semaphore = threading.Semaphore(1)
        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher('facebook', 'dump_file', semaphore)
        cf.run()
        self.assertTrue(semaphore.acquire(False))

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmpd = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpd)

    @mock.patch('crawlcrunch.url_open')
    def test_only_company_fetcher(self, urlopen):
        content = StringIO()
        json.dump({'foo': 'bar'}, content)
        content.seek(0)
        urlopen.return_value = content
        dump_file = os.path.join(self.tmpd, 'dump.json.gz')
        from crawlcrunch.crawler import CompanyFetcher
        cf = CompanyFetcher('facebook', 
                            dump_file,
                            threading.Semaphore(1))
        cf.run()
        urlopen.assert_called_once_with(
            'http://api.crunchbase.com/v/1/company/facebook.js'
            )
        with GzipFile(dump_file) as fp:
            self.assertEqual(json.load(fp), {'foo': 'bar'})

    @mock.patch('crawlcrunch.url_open')
    def test_crawler_and_company_fetcher(self, urlopen):
        content = StringIO()
        json.dump({'foo': 'bar'}, content)
        content.seek(0)
        urlopen.return_value = content
        from crawlcrunch.crawler import Crawler
        from crawlcrunch.model import CompaniesList
        dst_dir = LocalFilesDir(self.tmpd)
        cl = CompaniesList(dst_dir)
        cl.data.append('facebook')
        crawler = Crawler(cl, dst_dir)
        crawler.crawl()
        urlopen.assert_called_once_with(
            'http://api.crunchbase.com/v/1/company/facebook.js'
            )
        with GzipFile(os.path.join(self.tmpd, 'facebook.json.gz')) as fp:
            self.assertEqual(json.load(fp), {'foo': 'bar'})

if __name__ == '__main__': # pragma: no cover
    unittest.main()
