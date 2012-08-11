# -*- coding: utf-8 -*-

import sys

py_version = sys.version_info[:2]
PY3 = sys.version_info[0] == 3

if py_version == (2, 6): # pragma: no cover
    import gzip
    class GzipFile(gzip.GzipFile):
        def __enter__(self):
            return self
        def __exit__(self, *exc_info):
            return True
elif PY3: # pragma: no cover
    import io
    import gzip
    class GzipFile(gzip.GzipFile):
        def __enter__(self):
            return io.TextIOWrapper(self, encoding='UTF-8')
        def __exit__(self, *exc_info):
            return True
else:
    from gzip import GzipFile

try:
    from StringIO import StringIO
except ImportError: # pragma: no cover
    from io import StringIO

if PY3: # pragma: no cover
    from urllib.request import urlopen as url_open
else:
    from urllib2 import urlopen as url_open

if PY3: # pragma: no cover
    from collections import UserList
else:
    from UserList import UserList
