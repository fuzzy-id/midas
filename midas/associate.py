# -*- coding: utf-8 -*-
""" Provides ways to associate CrunchBase data and Alexa Top1M
sites. The main work is done via an :class:`AssociationTree` instance.

The idea is to built a tree from either the domain part of
:meth:`crawlcrunch.model.db.Company.homepage_url` or the domain part
of the Alexa Top1M sites . 
"""


import collections

import midas.tools as md_tools
import midas.statistics as md_stats

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

    def map(self, iterable, extract_func=None):
        if extract_func is None:
            extract_func = lambda a: a
        result = dict()
        for item in iterable:
            leafs = self.associate(extract_func(item))
            if leafs is not None:
                result[item] = leafs
        return result

def associate_companies_to_sites(tree=None, comps=None, sites=None):
    if tree is None:
        tree = grow_tree_from_companies(comps)
    if sites is None:
        sites = md_tools.iter_interesting_sites()
    return tree.map(sites, md_tools.domain)

def associate_sites_to_companies(tree=None, sites=None, comps=None):
    if tree is None:
        tree = grow_tree_from_sites(sites)
    if comps is None:
        comps = md_tools.iter_interesting_companies()
    return tree.map(sites, md_tools.domain)

def grow_tree_from_companies(comps=None):
    if comps is None:
        comps = md_stats.iter_interesting_companies()
    return grow_tree_from_sites_or_companies(comps)

def grow_tree_from_sites(sites=None):
    if sites is None:
        sites = md_stats.iter_sites_of_interest()
    return grow_tree_from_sites_or_companies(sites)

def grow_tree_from_sites_or_companies(iterable):
    tree = AssociationTree(split_domain)
    for item in iterable:
        tree.grow(item, md_tools.domain(item))
    return tree

def split_domain(site):
    return tuple(reversed(site.rsplit('.', 1)))
