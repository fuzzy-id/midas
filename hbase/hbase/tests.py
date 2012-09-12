# -*- coding: utf-8 -*-

from hbase.compat import PY26

if PY26:
    import unittest2 as unittest
else:
    import unittest


