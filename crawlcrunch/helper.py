# -*- coding: utf-8 -*-

from crawlcrunch.compat import comp_unicode

def determine_type_flat(obj):
    """ Queries a type and returns a map of the object with the named
    fields and their types.
    """ 
    if obj is None:
        return None
    elif isinstance(obj, str) or isinstance(obj, comp_unicode):
        return str
    elif isinstance(obj, int):
        return int
    elif isinstance(obj, float):
        return float
    elif isinstance(obj, list):
        return list(map(type, obj))
    elif isinstance(obj, dict):
        return dict(( (k, type(obj[k]))
                      for k in obj.keys() ))
    raise NotImplementedError('Unknown type {0!r}'.format(obj))

def merge_type_descr(a, b):
    if a is None:
        return b
    elif b is None:
        return a
    elif type(a) is not type(b):
        raise TypeError(
            'Not the same type, {0!r} and {1!r}'.format(a, b))
    elif a in (dict, list, str, int, float, comp_unicode):
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
    raise NotImplementedError('Unknown type {0!r}'.format(a))
