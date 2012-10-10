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

    def collect_buckets_of_single_branches(self):
        if len(self) == 0:  # The end of a branch
            for l in self.leafs:
                yield (l, self.bucket.values())
        elif len(self) == 1:  # We start collecting
            for leaf_bucket in \
                    self.values()[0].collect_buckets_of_single_branches():
                leaf_bucket[1].extend(self.bucket.values())
                yield leaf_bucket
        else:
            for branch in self.itervalues():
                for leaf_bucket in \
                        branch.collect_buckets_of_single_branches():
                    yield leaf_bucket

def domain_split_func(site):
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

def relate_with_sites(tree, sites=None):
    if sites is None:
        sites = md_stats.get_sites()
    result = dict()
    for s in sites:
        l = tree.relate(s)
        if l is not None:
            result[s] = l
    return result

def fill_with_sites(tree, sites=None):
    if sites is None:
        sites = md_stats.get_sites()
    for site in sites:
        domain = site.split('/', 1)[0]
        tree.fill(site, domain)
