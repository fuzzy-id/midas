# -*- coding: utf-8 -*-

import threading

from crawlcrunch.tests import unittest

class StdLibTests(unittest.TestCase):

    def test_semaphore_behaviour(self):
        semaphore = threading.Semaphore(1)
        semaphore.acquire()
        self.assertFalse(semaphore.acquire(False))
        semaphore.release()
        self.assertTrue(semaphore.acquire(False))
        
class MockTests(unittest.TestCase):

    def test_setting_return_values(self):
        import mock
        m = mock.MagicMock()
        m.get('companies').not_local.return_value = []
        companies = m.get('companies')
        self.assertEqual(companies.not_local(), [])

    def test_sub_mocks(self):
        import mock
        m = mock.MagicMock()
        companies = m.get('companies')
        companies.update()
        m.get('companies').update.assert_called_once_with()
