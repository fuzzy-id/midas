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
            fetcher = CompanyFetcher(
                self.inst_list.get(inst),
                self.semaphore)
            fetcher.start()
        # Wait 'til all threads finished
        for _ in range(self.num_threads):
            self.semaphore.acquire()


class CompanyFetcher(threading.Thread):

    def __init__(self, company, semaphore):
        super(CompanyFetcher, self).__init__()
        self.company = company
        self.semaphore = semaphore

    def run(self):
        try:
            self.company.update()
        except HTTPError as e:
            if e.code == 404:
                logging.critical(
                    '{0}: Got 404'.format(self.company.name))
            else:
                logging.exception(e)
        except Exception as e:
            logging.critical(
                '{0}: An exception occured'.format(self.company.name))
            logging.exception(e)
        finally:
            self.semaphore.release()
