# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch.compat import UserList
from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import url_open

class LocalFilesDir(object):

    suffix = '.json.gz'

    def __init__(self, path):
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        path = os.path.normpath(path)
        self.path = path

    def exists(self):
        return os.path.isdir(self.path)

    def expand(self, fname):
        return os.path.join(self.path, 
                            '{0}{1}'.format(fname, self.suffix))

    def get(self, name):
        local_file = self.get_object(name)
        return Company(name, local_file)

    def get_object(self, name):
        fname = self.expand(name)
        return ZippedJsonFile(fname)

class Company(object):
    
    def __init__(self, name, local_data):
        self.name = name
        self.local_data = local_data
    
    def is_local(self):
        return self.local_data.exists()

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

class CrunchBaseFetcherMixin(object):
    """ A base class that sums up the general ways to fetch data from
    crunchbase.
    """
    companies_list_url = 'http://api.crunchbase.com/v/1/companies.js'
    company_url_tpl = 'http://api.crunchbase.com/v/1/company/{0}.js'

    def query_url(self): # pragma: no cover
        raise NotImplementedError()

    def fetch(self):
        logging.info('Fetching {0}'.format(self.name))
        content = url_open(self.query_url())
        return json.load(content)

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
