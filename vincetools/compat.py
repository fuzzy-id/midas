# -*- coding: utf-8 -*-
""" This module fills the gap between Python 2.6 upwards to Python 3
since version 3.2.
"""

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

if PY3K:  # pragma: no cover
    from io import StringIO
else:
    from StringIO import StringIO

if PY26:  # pragma: no cover
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

if PY3K:  # pragma: no cover
    from collections import UserList
else:
    from UserList import UserList

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

if PY3K:  # pragma: no cover
    from configparser import ConfigParser
else:
    from ConfigParser import SafeConfigParser

    class ConfigParser(SafeConfigParser):

        def read_string(self, s):
            """ Puts the string `s` into a :class:`StringIO.StringIO`
            instance and passes it to :meth:`readfp`.
            """
            buf = StringIO(s)
            buf.seek(0)
            self.readfp(buf)

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
