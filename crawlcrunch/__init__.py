# -*- coding: utf-8 -*-

import json
import logging
import os.path

from crawlcrunch.compat import GzipFile
from crawlcrunch.compat import url_open

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

class CrunchBaseFetcherBase(object):
    """ A base class that sums up the general ways to fetch data from
    crunchbase.
    """
    companies_list_url = 'http://api.crunchbase.com/v/1/companies.js'
    company_url_tpl = 'http://api.crunchbase.com/v/1/company/{0}.js'

    def query_url(self):
        raise NotImplementedError()

    def fetch(self):
        logging.info('Fetching {0}'.format(self.name))
        content = url_open(self.query_url())
        return json.load(content)
