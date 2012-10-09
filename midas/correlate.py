# -*- coding: utf-8 -*-

import collections
import operator

from midas.compat import imap

import midas.tools as md_tools
import midas.statistics as md_stats

class BucketTree(dict):

    def __init__(self, splitfunc, name='root'):
        dict.__init__(self)
        self.splitfunc = splitfunc
        self.name = name
        self.leafs = []
        self.bucket = collections.defaultdict(list)

    def grow(self, item, key):
        if key is None:
            self.leafs.append(item)
            return
        split = self.splitfunc(key)
        if len(split) == 2:
            head, tail = split 
        else:
            head, tail = split[0], None
        if head not in self:
            self[head] = BucketTree(self.splitfunc, head)
        self[head].grow(item, tail)

    def fill(self, item, key):
        if key is None:
            self.bucket[None].append(item)
            return
        split = self.splitfunc(key)
        if len(split) == 2:
            head, tail = split
        else:
            head, tail = split[0], None
        if head not in self:
            self.bucket[head].append(item)
        else:
            self[head].fill(item, tail)

    def query(self, constraint):
        if constraint(self) > 0:
            yield self
        for branch in self.itervalues():
            for r in branch.query(constraint):
                yield r


def domain_split_func(site):
    return tuple(reversed(site.rsplit('.', 1)))

def get_all_urls(company):
    if company.homepage_url is not None and len(company.homepage_url) > 0:
        yield company.homepage_url
    if len(company.external_links) > 0:
        for link in company.external_links:
            yield link.external_url

def companies_grown_tree(comps=None):
    if comps is None:
        comps = md_stats.all_companies()
    tree = BucketTree(domain_split_func)
    for c in comps:
        for url in get_all_urls(c):
            tree.grow(c, md_tools.netloc(url).lower())
    return tree

def fill_with_sites(tree, sites=None):
    if sites is None:
        sites = imap(operator.attrgetter('site'), md_stats.get_site_counts())
    for site in sites:
        domain = site.split('/', 1)[0]
        tree.fill(site, domain)
