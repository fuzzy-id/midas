# -*- coding: utf-8 -*-

import shelve

from midas.scripts import MDCommand


class GeneratePositiveSamples(MDCommand):
    """
    Extract sites and tstamps from restrictions shelf.
    """

    def add_argument(self):
        self.parser.add_argument('shelf', help='The restrictions shelf.')

    def run(self):
        shelf = shelve.open(self.args.shelf)
        for restr in shelf.values():
            self.out('{0}\t{1:%Y-%m-%d}'.format(restr.site, restr.tstamp))
