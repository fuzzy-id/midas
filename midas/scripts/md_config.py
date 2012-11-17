# -*- coding: utf-8 -*-

import logging
import sys

from midas.scripts import MDCommand

import midas.config as md_cfg

class MDConfig(MDCommand):
    """ Read all configuration files, print the final configuration
    and exit. 

    This can be used to see how a configuration file (e.g. a job file)
    alters the whole configuration or to generate a default
    configuration file which is going to be altered in a second step.
    """

    POS_ARG = { 'dest': 'job_cfg',
                'nargs': '?',
                'metavar': 'FILE',
                'help': 'additional configuration file to read'}

    out = sys.stdout

    def __init__(self, argv):
        MDCommand.__init__(self, argv)
        if self.args.job_cfg:
            md_cfg.read(self.args.job_cfg)

    def run(self):
        md_cfg.get_configparser().write(self.out)
