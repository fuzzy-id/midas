# -*- coding: utf-8 -*-

import logging
import threading

from midas.compat import HTTPError
from midas.compat import Queue
from midas.crunchbase_company import CompanyList

import midas.scripts


class FetchCrunchbaseCompanies(midas.scripts.MDCommand):
    """
    Crawl the companies information from crunchbase.com and save it
    locally.
    """
    def add_argument(self):
        self.parser.add_argument('-p', '--num_threads', default=1,
                                 help='How many threads should crawl in parallel')
        self.parser.add_argument('location', 
                                 action=midas.scripts.CheckDirectoryAction,
                                 help='The location to save the crawled data')

    def run(self):
        if self.args.quiet:
            log_level = logging.CRITICAL
        else:
            log_level = logging.INFO
        logging.basicConfig(level=log_level)
        cl = CompanyList(self.args.location)
        logging.info('Updating CompanyList')
        cl.update()
        q = Queue()
        for _ in range(self.args.num_threads):
            t = Fetcher(q)
            t.daemon = True
            t.start()
        for company in cl.list_not_local():
            q.put(company)
        q.join()
        return 0


class Fetcher(threading.Thread):

    def __init__(self, queue):
        super(Fetcher, self).__init__()
        self.q = queue
        self.inst = None

    def run(self):
        while True:
            self.inst = self.q.get()
            logging.info('{0}: Updating'.format(self.inst))
            self.make_update(0)
            self.q.task_done()

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
