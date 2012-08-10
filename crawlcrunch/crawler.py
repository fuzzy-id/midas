# -*- coding: utf-8 -*-

import json
import threading
import urllib2

from crawlcrunch.compat import GzipFile

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
        self.dst = dst
        self.semaphore = semaphore

    def run(self):
        content = urllib2.urlopen(self.query_url())
        js = json.load(content)
        with GzipFile(self.dst, 'wb') as fp:
            json.dump(js, fp)
        self.semaphore.release()

    def query_url(self):
        return 'http://api.crunchbase.com/v/1/company/{0}.js'.format(
            self.company)
