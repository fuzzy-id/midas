# -*- coding: utf-8 -*-

import collections

import midas.tools as md_tools

class Parent(object):

    def __init__(self, name=None):
        self.branches = {}
        self.name = name
        self.values = []
        self.fulls = []

    def add_branch(self, site, full):
        if site == '':
            self.fulls.append(full)
            return
        split = site.rsplit('.', 1)
        if len(split) == 1:
            head, tail = '', split[0]
        else:
            head, tail = split
        if tail not in self.branches:
            self.branches[tail] = Parent(tail)
        self.branches[tail].add_branch(head, full)

    def add_value(self, site):
        if site == '':
            self.values.append(site)
            return
        split = site.rsplit('.', 1)
        if len(split) == 1:
            head, tail = '', split[0]
        else:
            head, tail = split
        if tail not in self.branches:
            self.values.append(site)
        else:
            self.branches[tail].add_value(head)

def build_tree(sites):
    root = Parent()
    for s in sites:
        try:
            domain, _ = s.lower().split('/', 1)
        except ValueError:
            domain = s.lower()
        root.add_branch(domain, s)
    return root
