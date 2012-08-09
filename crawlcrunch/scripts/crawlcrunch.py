# -*- coding: utf-8 -*-

import optparse
import sys

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
        if not self.args:
            self.out('You must provide a destination directory')
            return 2

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print msg
