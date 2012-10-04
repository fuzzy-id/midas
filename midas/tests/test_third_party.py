# -*- coding: utf-8 -*-

from midas.compat import StringIO
from midas.compat import ConfigParser
from midas.tests import unittest

class ConfigParserBehaviorTests(unittest.TestCase):

    def test_interpretation_of_None(self):
        buf = StringIO('\n'.join(['[foo]', 'bar = None', 'files']))
        buf.seek(0)
        cp = ConfigParser()
        cp.readfp(buf)
        self.assertEqual(cp.get('foo', 'bar'), 'None')
        self.assertIsNone(cp.get('foo', 'files'))
