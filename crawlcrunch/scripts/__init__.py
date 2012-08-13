# -*- coding: utf-8 -*-
import os.path

class CCBaseCommand(object):

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.options, self.args = self.parser.parse_args(argv[1:])

    def check_args(self):
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
        return 0

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print(msg)

