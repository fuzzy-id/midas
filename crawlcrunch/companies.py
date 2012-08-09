# -*- coding: utf-8 -*-

import gzip
import json
import os.path

class CompaniesList(object):
    
    def __init__(self, destination):
        self.destination = destination
        self.companies_file = os.path.join(self.destination, 
                                           'companies.json.gz')
        self.companies = None

    def create_list(self):
        with gzip.GzipFile(os.path.join(self.companies_file)) as fp:
            companies_js = json.load(fp)
        self.companies = [ company['permalink'] 
                           for company in companies_js ]
