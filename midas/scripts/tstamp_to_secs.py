# -*- coding: utf-8 -*-

import datetime
import time
import os

from midas.scripts import CheckDirectoryAction
from midas.scripts import MDCommand

FMT = 'top_1m_%Y-%m-%d'

class TstampToSecs(MDCommand):
    """
    Extracts the date of every Alexa file and generates the according
    seconds since epoch.
    """

    def add_argument(self):
        self.parser.add_argument(
            'alexa_files', action=CheckDirectoryAction,
            help='The directory where the unzipped Alexa files reside.'
            )

    def run(self):
        for f in sorted(os.listdir(self.args.alexa_files)):
            date = datetime.datetime.strptime(f, FMT)
            secs = time.mktime(date.timetuple())
            _, _, tstamp = f.strip().split('_')
            self.out('{0}\t{1}'.format(tstamp, int(secs)))
