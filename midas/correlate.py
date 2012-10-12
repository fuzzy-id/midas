# -*- coding: utf-8 -*-

import collections

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
        head, tail = self._filled_split(key)
        if head not in self:
            self[head] = BucketTree(self.splitfunc, head)
        self[head].grow(item, tail)

    def fill(self, item, key):
        if key is None:
            self.bucket[None].append(item)
            return
        head, tail = self._filled_split(key)
        if head not in self:
            self.bucket[head].append(item)
        else:
            self[head].fill(item, tail)

    def relate(self, key):
        if key is None:
            if len(self.leafs) > 0:  # definite relation
                return self.leafs
            elif len(self) == 1:  # relation is further down
                return self.values()[0].relate(key)
            else:  # No definite relation!
                return None
        else:
            head, tail = self._filled_split(key)
            if head in self:  # propagate
                return self[head].relate(tail)
            return self.relate(None)

    def _filled_split(self, key):
        split = self.splitfunc(key)
        if len(split) == 2:
            return split 
        else:
            return (split[0], None)
        
    def query(self, constraint):
        if constraint(self) > 0:
            yield self
        for branch in self.itervalues():
            for r in branch.query(constraint):
                yield r

def split_domain(site):
    return tuple(reversed(site.rsplit('.', 1)))

def get_all_urls(company):
    if company.homepage_url is not None and len(company.homepage_url) > 0:
        yield company.homepage_url

def companies_grown_tree(comps=None):
    if comps is None:
        comps = md_stats.companies_of_interest()
    tree = BucketTree(domain_split_func)
    for c in comps:
        for url in get_all_urls(c):
            tree.grow(c, md_tools.netloc(url).lower())
    return tree

def sites_grown_tree(sites=None):
    if sites is None:
        sites = md_stats.sites_of_interest()
    tree = BucketTree(domain_split_func)
    for site in sites:
        domain = site_domain(site)
        tree.grow(site, domain)
    return tree

def relate_with_sites(tree, sites=None):
    if sites is None:
        sites = md_stats.get_interesting_sites()
    result = dict()
    for s in sites:
        l = tree.relate(site_domain(s))
        if l is not None:
            result[s] = l
    return result

def relate_with_companies(tree, companies=None):
    if companies is None:
        companies = md_stats.companies_of_interest()
    result = dict()
    for company in companies:
        for url in get_all_urls(company):
            l = tree.relate(md_tools.netloc(url).lower())
            if l is not None:
                result[url] = l
    return result

def fill_with_sites(tree, sites=None):
    if sites is None:
        sites = md_stats.get_sites()
    for site in sites:
        domain = site_domain(site)
        tree.fill(site, domain)

def site_domain(site):
    return site.split('/', 1)[0].lower()
