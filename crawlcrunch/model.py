# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch.compat import UserList
from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import url_open

class LocalFilesDir(object):
    """ This is the root object of all data traversal.
    """ 

    suffix = '.json.gz'

    def __init__(self, path):
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        path = os.path.normpath(path)
        self.path = path
        self.nodes = {}

    def exists(self):
        return os.path.isdir(self.path)

    def expand(self, fname):
        return os.path.join(self.path, 
                            '{0}{1}'.format(fname, self.suffix))

    def get(self, name):
        if self.nodes.get(name, None) is None:
            local_data = self.get_local_data(name)
            if name == 'companies':
                self.nodes[name] = CompanyList(self, local_data)
            else:
                self.nodes[name] = Company(local_data, name)
        return self.nodes[name]

    def get_local_data(self, name):
        fname = self.expand(name)
        return ZippedJsonFile(fname)

class ZippedJsonFile(object):
    """ Implements access to local stored data, which is realized via
    compressed (gzipped) JSON files.
    """

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
    """ A mixin that sums up the general way to fetch data from
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

class Node(object):
    """ Defines the interface to access data, both locally and network
    data.
    """ 
    
    def __init__(self, local_data, name):
        self.local_data = local_data
        self.name = name

    def load(self): # pragma: no cover
        raise NotImplementedError()

    def update(self):
        self.local_data.dump(self.fetch())
        self.load()

    def is_local(self):
        return self.local_data.exists()

class Company(Node, CrunchBaseFetcherMixin):

    def query_url(self):
        return self.company_url_tpl.format(self.name)

class CompanyList(UserList, Node, CrunchBaseFetcherMixin):

    def __init__(self, root, local_data, name='companies'):
        UserList.__init__(self)
        Node.__init__(self, local_data, name)
        self.root = root
    
    def load(self):
        self.local_data.load()
        self.data = [ company['permalink'] 
                      for company in self.local_data.data ]

    def not_local(self):
        for company_name in self:
            company = self.root.get(company_name)
            if not company.is_local():
                yield company_name

    def query_url(self):
        return self.companies_list_url
