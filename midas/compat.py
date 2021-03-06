# -*- coding: utf-8 -*-
""" 
This module fills the gap between Python 2.6 upwards to Python 3 since
version 3.2.
"""

import contextlib
import csv
import sys

#: True if the current interpreter is of version 2.6
PY26 = sys.version_info[:2] == (2, 6)
#: True if the current interpreter is of version 3
PY3K = sys.version_info[0] == 3

if PY3K:  # pragma: no cover
    str_type = str
else:
    str_type = (str, unicode)

if PY3K:  # pragma: no cover
    comp_bytes = bytes
else:
    comp_bytes = (lambda a, _: bytes(a))

if PY3K:  # pragma: no cover
    comp_unicode = str
else:
    comp_unicode = unicode

if PY3K:  # pragma: no cover
    d_iterkeys = dict.keys
    d_itervalues = dict.values
    d_iteritems = dict.items
else:
    d_iterkeys = dict.iterkeys
    d_itervalues = dict.itervalues
    d_iteritems = dict.iteritems

if PY3K:  # pragma: no cover
    imap = map
else:
    from itertools import imap

if PY3K:  # pragma: no cover
    ifilter = filter
else:
    from itertools import ifilter

if PY3K:
    irange = range
else:
    irange = xrange

if PY3K:  # pragma: no cover
    from io import StringIO
else:
    from StringIO import StringIO

if PY3K:  # pragma: no cover
    comp_input = input
else:
    comp_input = raw_input

if PY3K:  # pragma: no cover
    from queue import Queue
    from queue import Empty as QueueEmpty
else:
    from Queue import Queue
    from Queue import Empty as QueueEmpty

if PY3K:  # pragma: no cover
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

if PY3K:  # pragma: no cover
    from urllib.error import HTTPError
else:
    from urllib2 import HTTPError

if PY3K:  # pragma: no cover
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

if PY26:  # pragma: no cover
    import unittest2 as unittest
else:
    import unittest

if not PY3K:
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp

if PY3K:  # pragma: no cover
    def csv_file_reader(fname, *args, **kwargs):
        with open(fname, newline='') as fp:
            for row in csv.reader(fp, *args, **kwargs):
                yield row

    @contextlib.contextmanager
    def csv_file_writer(fname, *args, **kwargs):
        with open(fname, 'w', newline='') as fp:
            yield csv.writer(fp, *args, **kwargs)

else:
    def csv_file_reader(fname, *args, **kwargs):
        with open(fname, 'rb') as fp:
            for row in csv.reader(fp, *args, **kwargs):
                yield row

    @contextlib.contextmanager
    def csv_file_writer(fname, *args, **kwargs):
        with open(fname, 'wb') as fp:
            yield csv.writer(fp, *args, **kwargs)

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
