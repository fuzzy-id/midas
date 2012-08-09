# -*- coding: utf-8 -*-

import sys

py_version = sys.version_info[:2]

if py_version == 2.6: # pragma: no cover
    import unittest2 as unittest
else:
    import unittest
