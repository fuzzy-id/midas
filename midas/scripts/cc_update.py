# -*- coding: utf-8 -*-

import logging
import threading

from midas.compat import HTTPError
from midas.crunchbase_crawler import CompanyList

import midas.scripts


class CCUpdateCommand(midas.scripts.MDCommand):
    """
    Crawl the companies information from crunchbase.com and save it
    locally.
    """
    def add_argument(self):
        self.parser.add_argument('location', 
                                 action=midas.scripts.CheckDirectoryAction,
                                 help='the location to save the crawled data')

    def run(self):
        if self.args.quiet:
            log_level = logging.CRITICAL
        else:
            log_level = logging.INFO
        logging.basicConfig(level=log_level)
        cl = CompanyList(self.args.location)
        updater = Updater(cl)
        updater.run()
        return 0


class Updater(object):

    def __init__(self, inst_list, num_threads=1):
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
            elif tries < 2 and (e.code == 503 or e.code == 504):
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
