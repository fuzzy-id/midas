# -*- coding: utf-8 -*-
"""
Provides ways to associate CrunchBase data and Alexa Top1M sites. The
main work is done via an :class:`AssociationTree` instance.

The idea is to built a tree from either the domain part of
:meth:`crawlcrunch.model.db.Company.homepage_url` or the domain part
of the Alexa Top1M sites . 
"""

from midas.compat import d_iteritems
from midas.compat import d_itervalues
from midas.compat import imap
from midas.compat import str_type
from midas.compat import urlparse

from midas.pig_schema import COMPANY_PARSER
from midas.pig_schema import SITE_COUNT_PARSER

from midas.tools import count_by_key
from midas.tools import identity

from midas.scripts import MDCommand
from midas.scripts import StoreSingleFileOrDirectoryAction


class Associate(MDCommand):
    """ 
    Tries to associate sites from the Alexa Top 1M data-set with
    Companies from CrunchBase. The association is printed to stdout in
    the form 'Permalink[TAB]Site'.
    """

    def add_argument(self):
        self.parser.add_argument(
            'site_count', action=StoreSingleFileOrDirectoryAction,
            help='The directory where the site-count data resides'
            )
        self.parser.add_argument(
            'companies', action=StoreSingleFileOrDirectoryAction,
            help='The directory where the flattened and filtered CrunchBase companies reside'
            )

    def run(self):
        tree = AssociationTree(split_domain)
        for sc in imap(SITE_COUNT_PARSER, self.args.site_count):
            tree.grow(sc, domain(sc.site))

        companies = imap(COMPANY_PARSER, self.args.companies)
        s2c = tree.map(companies, lambda c: domain(c.hp))
        cnt = count_by_key(s
                           for l in d_itervalues(s2c) 
                           for s in l)
        for company, sites in d_iteritems(s2c):
            for site in sites:
                if cnt[site] == 1:
                    self.out('\t'.join([company.permalink, site.site]))


def split_domain(site):
    return tuple(reversed(site.rsplit('.', 1)))


def domain(company_or_site):
    """
    Return the domain part of a Alexa Top1M site or a URL.
    """
    if 'http' in company_or_site:                    # A full URL
        return urlparse(company_or_site).netloc.lower()
    return company_or_site.split('/', 1)[0].lower()  # Alexa Top1M site


class AssociationTree(dict):

    def __init__(self, splitfunc, name='root'):
        dict.__init__(self)
        self.splitfunc = splitfunc
        self.name = name
        self.leafs = []

    def grow(self, item, key):
        if key is None:
            self.leafs.append(item)
            return
        head, tail = self._filled_split(key)
        if head not in self:
            self[head] = AssociationTree(self.splitfunc, head)
        self[head].grow(item, tail)

    def associate(self, key):
        if key is None:
            if len(self.leafs) > 0:  # Definite relation
                return self.leafs
            elif len(self) == 1:     # Relation could be further down
                return next(iter(self.values())).associate(None)
            else:                    # No definite relation!
                return None
        else:
            head, tail = self._filled_split(key)
            if head in self:         # Propagate
                return self[head].associate(tail)
            return self.associate(None)

    def _filled_split(self, key):
        split = self.splitfunc(key)
        if len(split) == 2:
            return split 
        else:
            return (split[0], None)
        
    def query(self, constraint):
        if constraint(self):
            yield self
        for branch in self.values():
            for r in branch.query(constraint):
                yield r

    def map(self, iterable, extract_func=identity):
        result = dict()
        for item in iterable:
            leafs = self.associate(extract_func(item))
            if leafs is not None:
                result[item] = leafs
        return result
