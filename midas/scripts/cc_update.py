# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import os.path
import sys

from midas.crunchbase_crawler.crawler import Updater
from midas.crunchbase_crawler.model.db import DataBaseRoot
from midas.crunchbase_crawler.model.local_files import LocalFilesRoot

def main(argv=sys.argv):
    command = CCUpdateCommand(argv)
    return command.run()

class CheckDirectory(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace.sql and not os.path.isdir(values):
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
    parser.add_argument('--sql', action='store_true', default=False,
                        help='update a sql database, create it if not existent')

    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])
        self.args.verbosity = sum(self.args.verbosity)

    def run(self):
        logging.basicConfig(level=self.args.verbosity)
        if self.args.sql:
            root = DataBaseRoot(self.args.location)
        else:
            root = LocalFilesRoot(self.args.location)
        try:
            for cls_name in self.args.classes:
                cls_inst = root.get(cls_name)
                updater = Updater(cls_inst)
                updater.run()
        finally:
            if hasattr(root, 'clean_up'):
                root.clean_up()
        return 0
