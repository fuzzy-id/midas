# -*- coding: utf-8 -*-

from __future__ import print_function

from crawlcrunch.compat import comp_unicode

class ModelCreator(object):

    def __init__(self, objs, access):
        self.access = access
        self.objs = objs
        self.root = None
        self._children = {}

    def run(self):
        for obj in self.objs:
            attr = self.access(obj)
            new_descr = determine_type_flat(attr)
            self.root = merge_type_descr(self.root, new_descr)
        if type(self.root) is dict:
            for k in self.root:
                if self.root[k] in (dict, list, ):
                    func = self.make_access_function(k)
                    sub = ModelCreator(self.objs, func)
                    sub.run()
                    self._children[k] = sub.root

    def make_access_function(self, attribute):
        def func(o):
            old_attr = self.access(o)
            if old_attr is not None:
                return old_attr[attribute]
        return func

    def __getattr__(self, name):
        if name in self._children:
            return self._children[name]
        raise AttributeError(name)


def determine_description(root, access_function):
    companies = root.get('companies')
    companies.load()
    company = root.get(companies[0])
    company.load()
    descr = determine_type_flat(access_function(company))
    for company_name in companies.list_local():
        company = root.get(company_name)
        company.load()
        try:
            new_descr = determine_type_flat(access_function(company))
            print('Merging with {0}'.format(company.name))
            descr = merge_type_descr(new_descr, descr)
        except Exception as e:
            print('Got an exception: {0!s}'.format(e))
            return descr
    return descr

def determine_type_flat(obj):
    """ Queries a type and returns a map of the object with the named
    fields and their types.
    """ 
    t = determine_simple_type(obj)
    if t is list:
        return list(map(type, obj))
    elif t is dict:
        return dict(( (k, determine_simple_type(obj[k]))
                      for k in obj.keys() ))
    else:
        return t

def determine_simple_type(obj):
    if obj is None:
        return None
    elif isinstance(obj, str) or isinstance(obj, comp_unicode):
        return str
    elif isinstance(obj, int):
        return int
    elif isinstance(obj, float):
        return float
    elif isinstance(obj, dict):
        return dict
    elif isinstance(obj, list):
        return list
    raise NotImplementedError('Unknown type {0!r}'.format(obj))

def merge_type_descr(a, b):
    if a is None:
        return b
    elif b is None:
        return a
    elif type(a) is not type(b):
        raise TypeError(
            'Not the same type, {0!r} and {1!r}'.format(a, b))
    elif a in (dict, list, str, int, float):
        return a
    elif isinstance(a, dict):
        result = {}
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        diff = a_keys.difference(b_keys).union(b_keys.difference(a_keys))
        if len(diff) != 0:
            raise ValueError(
                'Found additional indices: {0}'.format(diff))
        for k in a.keys():
            result[k] = merge_type_descr(a[k], b[k])
        return result
    elif isinstance(a, list):
        # First we'll assume that the list is actually a tupel
        if len(a) == 0:
            return b
        elif len(b) == 0:
            return a
        elif len(a) == len(b):
            return a
        # The next assumption is: it is actually a list!
        # Hence, all the objects should be of the same type
        t = a[0]
        for i in a + b:
            if i is not t:
                raise ValueError(
                    'Differing types: {0} is no {1}.'.format(i, t))
        return [t]
    raise NotImplementedError('Unknown type {0!r}'.format(a))
