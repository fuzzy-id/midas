# -*- coding: utf-8 -*-

import json
import logging
import threading

from crawlcrunch import ZippedJsonFile
from crawlcrunch import CrunchBaseFetcherMixin
from crawlcrunch.compat import url_open

class Crawler(object):

    def __init__(self, companies_list, dst_dir, num_threads=20):
        self.companies = companies_list
        self.dst_dir = dst_dir
        self.num_threads = num_threads
        self.semaphore = threading.Semaphore(num_threads)
        self.threads = []

    def crawl(self):
        for company in self.companies.not_local():
            self.semaphore.acquire()
            fetcher = CompanyFetcher(
                company, 
                self.dst_dir.expand(company),
                self.semaphore)
            fetcher.start()
        # Wait 'til all threads finished
        for _ in range(self.num_threads):
            self.semaphore.acquire()

class CompanyFetcher(threading.Thread, CrunchBaseFetcherMixin):

    def __init__(self, company, dst, semaphore):
        super(CompanyFetcher, self).__init__()
        self.name = company
        self.zipf = ZippedJsonFile(dst)
        self.semaphore = semaphore

    def run(self):
        try:
            self.zipf.dump(self.fetch())
        except Exception as e:
            logging.exception(e)
        finally:
            self.semaphore.release()

    def query_url(self):
        return self.company_url_tpl.format(self.name)
