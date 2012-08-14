def determine_type(obj):
    """ Recursively queries a type and returns a map of the object
    with the named fields and their types.
    """ 
    if obj is None:
        return None
    elif isinstance(obj, str):
        return str
    elif isinstance(obj, int):
        return int
    elif isinstance(obj, float):
        return float
    elif isinstance(obj, list):
        return list(map(determine_type, obj))
    elif isinstance(obj, dict):
        return dict(( (k, determine_type(obj[k]))
                      for k in obj.keys() ))
    raise NotImplemented('Unknown type {0!r}'.format(obj))
