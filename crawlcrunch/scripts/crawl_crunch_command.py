# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import optparse
import os.path
import sys

from crawlcrunch.companies import CompaniesList
from crawlcrunch.crawler import Crawler

def main(argv=sys.argv, quiet=False):
    command = CrawlCrunchCommand(argv, quiet)
    return command.run()

class CrawlCrunchCommand(object):
    
    description = "Crawl the companies information from crunchbase.com"
    usage = "usage: %prog [options] dest_dir"
    parser = optparse.OptionParser(usage, description=description)

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.options, self.args = self.parser.parse_args(argv[1:])

    def run(self):
        if len(self.args) == 0:
            self.out('You must provide a destination directory')
            return 2
        elif len(self.args) > 1:
            self.out(
                'You must provide one destination directory, not {0}.'.format(len(self.args)))
            return 2
        elif not os.path.isdir(self.args[0]):
            self.out("The directory '{0}' does not exist!".format(
                    self.args[0]))
            self.out('Please, create it first.')
            return 2
        basedir = os.path.expanduser(self.args[0])
        basedir = os.path.abspath(basedir)
        basedir = os.path.normpath(basedir)
        logging.basicConfig(level=logging.DEBUG)
        cl = CompaniesList(basedir)
        cl.create_list()
        crawler = Crawler(cl)
        crawler.crawl()
        return 0

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print(msg)
