# -*- coding: utf-8 -*-

import sys

PY_VERSION = sys.version_info[:2]

PY26 = PY_VERSION == (2, 6)

if PY26:  # pragma: no cover
    import zipfile
    class ZipFile(zipfile.ZipFile):
        
        def __enter__(self):
            return self

        def __exit__(self, *exc_inf):
            return True
else:
    from zipfile import ZipFile

if PY26:  # pragma: no cover
    import gzip
    class GzipFile(gzip.GzipFile):

        def __enter__(self):
            return self

        def __exit__(self, *exc_inf):
            return True
else:
    from gzip import GzipFile

try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover
    from io import StringIO
