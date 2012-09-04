# -*- coding: utf-8 -*-

import logging
import json

import crawlcrunch.compat


class CrunchBaseFetcherMixin(object):
    """ A mixin that sums up the general way to fetch data from
    crunchbase.
    """
    to_replace = ('\x00', '\x03', '\x0b', '\x0e',
                  '\x12', '\x14', '\x1d', '\x1e', '\x1f')
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
        response = crawlcrunch.compat.urlopen(self.query_url())
        content = response.read()
        s = content.decode('utf-8')
        # Some companies have control chars in theire description
        # *sigh*
        s = self.replace_control_chars(s)
        return json.loads(s)


