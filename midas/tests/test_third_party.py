# -*- coding: utf-8 -*-

from midas.compat import StringIO
from midas.compat import ConfigParser
from midas.tests import unittest

class ConfigParserBehaviorTests(unittest.TestCase):

    def test_interpretation_of_None(self):
        cp = ConfigParser()
        cp.read_string('\n'.join(['[foo]', 'bar = None']))
        self.assertEqual(cp.get('foo', 'bar'), 'None')

