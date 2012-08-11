# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch import ZippedJsonFile
from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import UserList
from crawlcrunch.compat import url_open

class CompaniesList(UserList):
    
    def __init__(self, destination):
        super(CompaniesList, self).__init__()
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

    def fetch_list(self):
        logging.info('Fetching the companies list.')
        content = url_open(
            'http://api.crunchbase.com/v/1/companies.js')
        self.zipf.dump(json.load(content))
