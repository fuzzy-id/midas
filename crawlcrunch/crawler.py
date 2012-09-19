# -*- coding: utf-8 -*-

import logging
import threading

from crawlcrunch.compat import HTTPError


class Updater(object):

    def __init__(self, inst_list, num_threads=20):
        self.inst_list = inst_list
        self.num_threads = num_threads
        self.semaphore = threading.Semaphore(num_threads)

    def run(self):
        self.inst_list.update()
        for inst in self.inst_list.list_not_local():
            self.semaphore.acquire()
            fetcher = Fetcher(inst, self.semaphore)
            fetcher.start()
        # Wait 'til all threads finished
        for _ in range(self.num_threads):
            self.semaphore.acquire()


class Fetcher(threading.Thread):

    def __init__(self, inst, semaphore):
        super(Fetcher, self).__init__()
        self.inst = inst
        self.semaphore = semaphore

    def run(self):
        self.make_update(0)

    def make_update(self, tries=0):
        try:
            self.inst.update()
        except HTTPError as e:
            if e.code == 404:
                logging.critical(
                    '{0}: Got 404'.format(self.inst))
            elif e.code == 504 and tries < 2:
                logging.critical(
                    '{0}: Got 504 ({1} attempt[s])'.format(self.inst, tries + 1))
                self.make_update(tries + 1)
            else:
                logging.exception(e)
        except Exception as e:
            logging.critical(
                '{0}: An exception occured'.format(self.inst))
            logging.exception(e)
        finally:
            self.semaphore.release()
