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
    
