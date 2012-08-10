# -*- coding: utf-8 -*-

import threading

from crawlcrunch.compat import unittest

class StdLibTests(unittest.TestCase):

    def test_semaphore_behaviour(self):
        semaphore = threading.Semaphore(1)
        semaphore.acquire()
        self.assertFalse(semaphore.acquire(False))
        semaphore.release()
        self.assertTrue(semaphore.acquire(False))
        
