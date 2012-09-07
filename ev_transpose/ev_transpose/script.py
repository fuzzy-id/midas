# -*- coding: utf-8 -*-

import argparse
import sys


def main(argv=sys.argv):
    command = EvTranspose(argv)
    return command.run()

class EvTranspose(object):

    description = ""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('dst', help='the destination for the output files')
    parser.add_argument('zip_file', nargs='+', help='the zipped files to parse')
    
    def __init__(self, argv):
        self.args = self.parser.parse_args(argv[1:])

    def run(self):
        return 0
