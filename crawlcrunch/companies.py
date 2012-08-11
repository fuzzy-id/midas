# -*- coding: utf-8 -*-

import os.path

from crawlcrunch import ZippedJsonFile
from crawlcrunch import CrunchBaseFetcherMixin
from crawlcrunch.compat import UserList

class CompaniesList(UserList, CrunchBaseFetcherMixin):
    
    def __init__(self, dst_dir):
        super(CompaniesList, self).__init__()
        self.name = 'the companies list'
        self.dst_dir = dst_dir
        self.zipf = ZippedJsonFile(self.dst_dir.expand('companies'))

    def create_list(self):
        if not self.zipf.exists():
            self.zipf.dump(self.fetch())
        else:
            self.zipf.load()
        for company in self.zipf.data:
            company_file = self.dst_dir.expand(company['permalink'])
            if not os.path.isfile(company_file):
                self.data.append(company['permalink'])

    def query_url(self):
        return self.companies_list_url
