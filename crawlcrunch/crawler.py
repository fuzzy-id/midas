# -*- coding: utf-8 -*-

import json
import logging
import threading

from crawlcrunch.model import ZippedJsonFile
from crawlcrunch.model import CrunchBaseFetcherMixin
from crawlcrunch.compat import url_open

class Crawler(object):

    def __init__(self, root, num_threads=20):
        self.companies = root.get('companies')
        self.root = root
        self.num_threads = num_threads
        self.semaphore = threading.Semaphore(num_threads)
        self.threads = []

    def crawl(self):
        for company in self.companies.not_local():
            self.semaphore.acquire()
            fetcher = CompanyFetcher(
                self.root.get(company),
                self.semaphore)
            fetcher.start()
        # Wait 'til all threads finished
        for _ in range(self.num_threads):
            self.semaphore.acquire()

class CompanyFetcher(threading.Thread):

    def __init__(self, company, semaphore):
        super(CompanyFetcher, self).__init__()
        self.company = company
        self.semaphore = semaphore

    def run(self):
        try:
            self.company.update()
        except Exception as e:
            logging.exception(e)
        finally:
            self.semaphore.release()
