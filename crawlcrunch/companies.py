# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import UserList
from crawlcrunch.compat import url_open

class CompaniesList(UserList):
    
    def __init__(self, destination):
        super(CompaniesList, self).__init__()
        self.destination = destination
        self.companies_file = ZippedJsonFile(self.expand_fname('companies'))

    def create_list(self):
        if not self.companies_file.exists():
            self.fetch_list()
        else:
            self.companies_file.load()
        for company in self.companies_file.data:
            company_file = self.expand_fname(company['permalink'])
            if not os.path.isfile(company_file):
                self.data.append(company['permalink'])

    def expand_fname(self, fname):
        return os.path.join(self.destination, 
                            '{0}.json.gz'.format(fname))

    def fetch_list(self):
        logging.info('Fetching the companies list.')
        content = url_open(
            'http://api.crunchbase.com/v/1/companies.js')
        self.companies_file.dump(json.load(content))

class ZippedJsonFile(object):

    def __init__(self, path):
        self.path = path
        self.data = None

    def exists(self):
        return os.path.isfile(self.path)

    def load(self):
        with GzipFile(self.path, 'rb') as fp:
            self.data = json.load(fp)

    def dump(self, data=None):
        if data is not None:
            self.data = data
        with GzipFile(self.path, 'wb') as fp:
            json.dump(self.data, fp)
