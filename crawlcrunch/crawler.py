# -*- coding: utf-8 -*-

import json
import logging
import threading

from crawlcrunch import ZippedJsonFile
from crawlcrunch.compat import url_open

class Crawler(object):

    def __init__(self, companies_list, num_threads=20):
        self.companies = companies_list
        self.num_threads = num_threads
        self.semaphore = threading.Semaphore(num_threads)
        self.threads = []

    def crawl(self):
        for company in self.companies:
            self.semaphore.acquire()
            fetcher = CompanyFetcher(
                company, 
                self.companies.expand_fname(company),
                self.semaphore)
            fetcher.start()
        # Wait 'til all threads finished
        for _ in range(self.num_threads):
            self.semaphore.acquire()

class CompanyFetcher(threading.Thread):

    def __init__(self, company, dst, semaphore):
        super(CompanyFetcher, self).__init__()
        self.company = company
        self.zipf = ZippedJsonFile(dst)
        self.semaphore = semaphore

    def run(self):
        logging.info('Fetching company {0}'.format(self.company))
        try:
            content = url_open(self.query_url())
            js = json.load(content)
            self.zipf.dump(js)
        except Exception as e:
            logging.exception(e)
        finally:
            self.semaphore.release()

    def query_url(self):
        return 'http://api.crunchbase.com/v/1/company/{0}.js'.format(
            self.company)
