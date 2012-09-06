# -*- coding: utf-8 -*-

from ev_transpose.tests import IntegrationTestCase
from ev_transpose.tests import unittest

class ScriptTests(IntegrationTestCase):

    @unittest.skip('not implemented, yet')
    def test_reducer(self):
        from ev_transpose.scripts import reducer
        data = ['foo\t2012-09-05,1',
                'foo\t2012-09-03,1',
                'foo\t2012-09-06,3',
                'foo\t2012-09-04,2']
        sys.stdin.write('\n'.join(data))
        self.assertEqual(reducer(), 0)
        sys.stdout.seek(0)
        out = sys.stdout.getvalue()
        data.sort()
        expected = '\n'.join(data)
        self.assertEqual(out, expected)

