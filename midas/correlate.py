# -*- coding: utf-8 -*-

import collections

class Parent(object):

    def __init__(self, name=None):
        self.branches = {}
        self.name = name
        self.values = []
        self.node_cnt = 0

    def add_branch(self, site):
        if site == '':
            self.node_cnt += 1
            return
        split = site.rsplit('.', 1)
        if len(split) == 1:
            head, tail = '', split[0]
        else:
            head, tail = split
        if tail not in self.branches:
            self.branches[tail] = Parent(tail)
        self.branches[tail].add_branch(head)

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
        root.add_branch(s.lower())
    return root
