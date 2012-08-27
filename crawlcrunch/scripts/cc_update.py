# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import os.path
import sys

from crawlcrunch.crawler import Updater
from crawlcrunch.model.local_files import LocalFilesDir
from crawlcrunch.scripts import CCBaseCommand

def main(argv=sys.argv, quiet=False):
    command = CCUpdateCommand(argv, quiet)
    return command.run()

class CheckDirectory(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            parser.error("the directory '{0}' does not exist".format(
                    values))
        setattr(namespace, self.dest, values)


class CCUpdateCommand(CCBaseCommand):
    
    description = """Crawl the companies information from
crunchbase.com and save it locally, either in the file system or in a
database.
"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('location', action=CheckDirectory,
                        help='the location to save the crawled data')

    def run(self):
        root = LocalFilesDir(self.args.location)
        logging.basicConfig(level=logging.DEBUG)
        updater = Updater(root)
        updater.run()
        return 0
