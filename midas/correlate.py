# -*- coding: utf-8 -*-

import collections

import midas.tools as md_tools

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

def build_tree(sites):
    root = Parent()
    for s in sites:
        domain = s.lower().split('/', 1)[0]
        root.add_branch(domain, s)
    return root
