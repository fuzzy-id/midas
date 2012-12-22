# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import os.path
import sys
import threading

from midas.compat import HTTPError
from midas.crunchbase_crawler import CompanyList


def main(argv=sys.argv):
    command = CCUpdateCommand(argv)
    return command.run()

class CheckDirectory(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            parser.error("the directory '{0}' does not exist".format(
                    values))
        setattr(namespace, self.dest, values)


class CCUpdateCommand(object):
    
    description = """Crawl the companies information from
crunchbase.com and save it locally, either in the file system or in a
database.
"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('location', action=CheckDirectory,
                        help='the location to save the crawled data')
    parser.add_argument('classes', nargs='*', metavar='CLASS',
                        default=['companies'],
                        help="""update CLASS, available classes are:
'companies'; all available classes are updated by default""")
    parser.add_argument('-v', '--verbose', dest='verbosity', 
                        action='append_const', const=-10, 
                        help='be verbose, can be given multiple times',
                        default=[logging.getLevelName('INFO')])
    parser.add_argument('-q', '--quiet', dest='verbosity', 
                        action='append_const', const=10,
                        help='be quiet, can be given multiple times')

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self.args.verbosity = sum(self.args.verbosity)

    def run(self):
        logging.basicConfig(level=self.args.verbosity)
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
