# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch.compat import UserList
from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import url_open


class LocalFilesRoot(object):
    """ This is the root object of all data traversal.
    """

    suffix = '.json.gz'

    def __init__(self, path):
        self.path = path

    def expand(self, fname):
        return os.path.join(self.path,
                            '{0}{1}'.format(fname, self.suffix))

    def get(self, name):
        if name == 'companies':
            return CompanyList(self, self.path)
        else:
            local_data = self.get_local_data(name)
            return Company(local_data, name)

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
        if self.data is None:
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
    to_replace = ('\x00',
                  '\x03',
                  '\x0b',
                  '\x0e',
                  '\x12',
                  '\x14',
                  '\x1d',
                  '\x1e',
                  '\x1f',
                  )
    companies_list_url = 'http://api.crunchbase.com/v/1/companies.js'
    company_url_tpl = 'http://api.crunchbase.com/v/1/company/{0}.js'

    def query_url(self):  # pragma: no cover
        raise NotImplementedError()

    @classmethod
    def replace_control_chars(cls, s):
        for c in cls.to_replace:
            s = s.replace(c, '')
        return s

    def fetch(self):
        logging.info('Fetching {0}'.format(self.name))
        response = url_open(self.query_url())
        content = response.read()
        s = content.decode('utf-8')
        # Some companies have control chars in theire description
        # *sigh*
        s = self.replace_control_chars(s)
        return json.loads(s)


class Node(object):
    """ Defines the interface to access data, both locally and network
    data.
    """

    def __init__(self, local_data, name):
        self.local_data = local_data
        self.name = name

    def load(self):  # pragma: no cover
        raise NotImplementedError()

    def update(self):
        self.local_data.dump(self.fetch())
        self.load()

    def is_local(self):
        return self.local_data.exists()


class Company(Node, CrunchBaseFetcherMixin):

    def load(self):
        self.local_data.load()
        self.data = self.local_data.data

    def query_url(self):
        return self.company_url_tpl.format(self.name)


class CompanyList(CrunchBaseFetcherMixin):

    name='companies'

    def __init__(self, root, path):
        self.root = root
        self.path = path
        self._remote_nodes = set()

    def list_not_local(self):
        for company_name in self._remote_nodes:
            company = self.root.get(company_name)
            if not company.is_local():
                yield company_name

    def list_local(self):
        for company_file in os.listdir(self.path):
            company_name = company_file.split('.')[0]
            company = self.root.get(company_name)
            if company.is_local():
                yield company_name

    def get(self, company):
        return self.root.get(company)

    def query_url(self):
        return self.companies_list_url

    def update(self):
        data = self.fetch()
        for company in data:
            self._remote_nodes.add(company['permalink'])
