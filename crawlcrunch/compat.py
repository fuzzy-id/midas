# -*- coding: utf-8 -*-

import sys

py_version = sys.version_info[:2]

if py_version == (2, 6): # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

if py_version == (2, 6): # pragma: no cover
    import gzip
    class GzipFile(gzip.GzipFile):
        def __enter__(self):
            return self
        def __exit__(self, *exc_info):
            return True
else:
    from gzip import GzipFile
