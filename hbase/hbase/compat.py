# -*- coding: utf-8 -*-

import sys

PY_VERSION = sys.version_info[:2]
PY26 = PY_VERSION == (2, 6)
PY3K = PY_VERSION >= (3, 2)

if PY3K:  # pragma: no cover
    from urllib.request import Request
    from urllib.request import urlopen
else:
    from urllib2 import Request
    from urllib2 import urlopen
    
if PY3K:  # pragma: no cover
    comp_bytes = bytes
else:
    comp_bytes = lambda s, _: s

if PY26:  # pragma: no cover
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict
