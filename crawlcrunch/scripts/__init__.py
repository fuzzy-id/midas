# -*- coding: utf-8 -*-
import os.path

class CCBaseCommand(object):

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.args = self.parser.parse_args(argv[1:])

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print(msg)

