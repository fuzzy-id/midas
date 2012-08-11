# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch import ZippedJsonFile
from crawlcrunch import CrunchBaseFetcherBase
from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import UserList
from crawlcrunch.compat import url_open

class CompaniesList(UserList, CrunchBaseFetcherBase):
    
    def __init__(self, destination):
        super(CompaniesList, self).__init__()
        self.name = 'the companies list'
        self.destination = destination
        self.zipf = ZippedJsonFile(self.expand_fname('companies'))

    def create_list(self):
        if not self.zipf.exists():
            self.fetch_list()
        else:
            self.zipf.load()
        for company in self.zipf.data:
            company_file = self.expand_fname(company['permalink'])
            if not os.path.isfile(company_file):
                self.data.append(company['permalink'])

    def expand_fname(self, fname):
        return os.path.join(self.destination, 
                            '{0}.json.gz'.format(fname))

    def query_url(self):
        return self.companies_list_url
    
    def fetch_list(self):
        self.zipf.dump(self.fetch())
