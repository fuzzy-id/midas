# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import url_open

class CompaniesList(object):
    
    def __init__(self, destination):
        self.destination = destination
        self.companies_file = self.expand_fname('companies')
        self.companies = None

    def create_list(self):
        if not os.path.isfile(self.companies_file):
            self.fetch_list()
        with GzipFile(os.path.join(self.companies_file)) as fp:
            companies_js = json.load(fp)
        self.companies = []
        for company in companies_js:
            company_file = self.expand_fname(company['permalink'])
            if not os.path.isfile(company_file):
                self.companies.append(company['permalink'])

    def expand_fname(self, fname):
        return os.path.join(self.destination, 
                            '{0}.json.gz'.format(fname))

    def fetch_list(self):
        logging.info('Fetching the companies list.')
        content = url_open(
            'http://api.crunchbase.com/v/1/companies.js')
        js = json.load(content)
        with GzipFile(self.companies_file, 'wb') as fp:
            json.dump(js, fp)

    def __iter__(self):
        for company in self.companies:
            yield company
