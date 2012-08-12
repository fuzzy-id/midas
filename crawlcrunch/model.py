# -*- coding: utf-8 -*-

import os.path

from crawlcrunch import ZippedJsonFile
from crawlcrunch import CrunchBaseFetcherMixin
from crawlcrunch.compat import UserList

class CompaniesList(UserList, CrunchBaseFetcherMixin):
    
    def __init__(self, root):
        super(CompaniesList, self).__init__()
        self.name = 'the companies list'
        self.root = root
        self.local_data = self.root.get_object('companies')
    
    def load(self):
        self.local_data.load()
        self.data = [ company['permalink'] 
                      for company in self.local_data.data ]

    def update(self):
        self.local_data.dump(self.fetch())
        self.load()

    def not_local(self):
        for company_name in self:
            company = self.root.get(company_name)
            if not company.is_local():
                yield company_name

    def query_url(self):
        return self.companies_list_url
