# -*- coding: utf-8 -*-

import gzip
import json
import os.path

class CompaniesList(object):
    
    def __init__(self, destination):
        self.destination = destination
        self.companies_file = self.expand_fname('companies')
        self.companies = None

    def create_list(self):
        with gzip.GzipFile(os.path.join(self.companies_file)) as fp:
            companies_js = json.load(fp)
        self.companies = []
        for company in companies_js:
            company_file = self.expand_fname(company['permalink'])
            if not os.path.isfile(company_file):
                self.companies.append(company['permalink'])

    def expand_fname(self, fname):
        return os.path.join(self.destination, 
                            '{0}.json.gz'.format(fname))