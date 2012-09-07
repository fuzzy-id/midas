# -*- coding: utf-8 -*-

import sys

PY_VERSION = sys.version_info[:2]

if PY_VERSION == (2, 6):  # pragma: no cover
    import zipfile
    class ZipFile(zipfile.ZipFile):
        
        def __enter__(self):
            return self

        def __exit__(self, *exc_inf):
            return True
else:
    from zipfile import ZipFile

from gzip import GzipFile

try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover
    from io import StringIO
