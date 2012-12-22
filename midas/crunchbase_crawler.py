# -*- coding: utf-8 -*-

import json
import os.path

from midas.compat import GzipFile
from midas.compat import urlopen
from midas.compat import HTTPError


class CrunchBaseFetchable(object):
    """ A mixin that sums up the general way to fetch data from
    crunchbase.
    """
    TO_REPLACE = set(['\x00', '\x03', '\x0b', '\x0e',
                      '\x12', '\x14', '\x1d', '\x1e', '\x1f'])
    API_KEY = 'vqrwexbhj9s2d7fbzzj9cg57'

    def query_url(self):  # pragma: no cover
        raise NotImplementedError()

    @classmethod
    def replace_control_chars(cls, s):
        for c in cls.TO_REPLACE:
            s = s.replace(c, '')
        return s

    def fetch(self):
        response = urlopen(self.query_url())
        content = response.read()
        s = content.decode('utf-8')
        # Some companies have control chars in theire description
        # *sigh*
        s = self.replace_control_chars(s)
        return json.loads(s)


class CompanyList(CrunchBaseFetchable):

    name='companies'
    suffix = '.json.gz'

    def __init__(self, path):
        self.path = path
        self._remote_nodes = set()

    def list_not_local(self):
        for company_name in self._remote_nodes:
            company = self.get(company_name)
            if not company.is_local():
                yield company

    def list_local(self):
        for company_file in os.listdir(self.path):
            company_name = company_file.split('.')[0]
            company = self.get(company_name)
            if company.is_local():
                yield company

    def get(self, company_name):
        local_data = self.get_local_data(company_name)
        return Company(local_data, company_name)

    def expand(self, fname):
        return os.path.join(self.path,
                            '{0}{1}'.format(fname, self.suffix))

    def get_local_data(self, name):
        fname = self.expand(name)
        return ZippedJsonFile(fname)

    def query_url(self):
        return '?'.join(('http://api.crunchbase.com/v/1/companies.js',
                         'api_key={0}'.format(self.API_KEY)))

    def update(self):
        data = self.fetch()
        for company in data:
            self._remote_nodes.add(company['permalink'])


class Company(CrunchBaseFetchable):

    def __init__(self, local_data, name):
        self.local_data = local_data
        self.name = name

    def __str__(self):
        return 'Company( {0} )'.format(self.name)

    def update(self):
        self.local_data.dump(self.fetch())
        self.load()

    def is_local(self):
        return self.local_data.exists()

    def load(self):
        self.local_data.load()
        self.data = self.local_data.data

    def query_url(self):
        return '?'.join(('http://api.crunchbase.com/v/1/company/{0}.js',
                         'api_key={1}')).format(self.name, self.API_KEY)


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
                self.data = json.loads(fp.read().decode())

    def dump(self, data=None):
        if data is not None:
            self.data = data
        with GzipFile(self.path, 'wb') as fp:
            fp.write(json.dumps(self.data).encode())
