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
