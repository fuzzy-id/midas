# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import optparse
import sys

from crawlcrunch.crawler import Updater
from crawlcrunch.model.local_files import LocalFilesDir
from crawlcrunch.scripts import CCBaseCommand

def main(argv=sys.argv, quiet=False):
    command = CCUpdateCommand(argv, quiet)
    return command.run()

class CCUpdateCommand(CCBaseCommand):
    
    description = "Crawl the companies information from crunchbase.com"
    usage = "usage: %prog [options] dest_dir"
    parser = optparse.OptionParser(usage, description=description)

    def run(self):
        ret = self.check_args()
        if ret != 0:
            return ret
        root = LocalFilesDir(self.args[0])
        logging.basicConfig(level=logging.DEBUG)
        updater = Updater(root)
        updater.run()
        return 0
