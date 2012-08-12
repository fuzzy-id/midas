# -*- coding: utf-8 -*-

import os.path

from crawlcrunch import ZippedJsonFile
from crawlcrunch import CrunchBaseFetcherMixin
from crawlcrunch.compat import UserList

class CompaniesList(UserList, CrunchBaseFetcherMixin):
    
    def __init__(self, local_data):
        super(CompaniesList, self).__init__()
        self.name = 'the companies list'
        self.local_data = local_data
        self.zipf = self.local_data.get_object('companies')

    def create_list(self):
        if not self.zipf.exists():
            self.zipf.dump(self.fetch())
        else:
            self.zipf.load()
        for company in self.zipf.data:
            company_file = self.local_data.expand(company['permalink'])
            if not os.path.isfile(company_file):
                self.data.append(company['permalink'])

    def query_url(self):
        return self.companies_list_url
