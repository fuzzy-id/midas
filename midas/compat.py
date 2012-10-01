# -*- coding: utf-8 -*-

import sys

PY26 = sys.version_info[:2] == (2, 6)
PY3K = sys.version_info[0] == 3

if PY26:  # pragma: no cover
    import zipfile
    class ZipFile(zipfile.ZipFile):
        
        def __enter__(self):
            return self

        def __exit__(self, *exc_inf):
            self.close()
            return True
else:
    from zipfile import ZipFile

if PY26:  # pragma: no cover
    import gzip
    class GzipFile(gzip.GzipFile):

        def __enter__(self):
            return self

        def __exit__(self, *exc_inf):
            self.close()
            return True
else:
    from gzip import GzipFile

if PY3K:  # pragma: no cover
    imap = map
else:
    from itertools import imap

if PY3K:  # pragma: no cover
    ifilter = filter
else:
    from itertools import ifilter

if PY3K:  # pragma: no cover
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover
    from io import StringIO
