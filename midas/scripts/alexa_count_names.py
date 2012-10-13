# -*- coding: utf-8 -*-

import logging

from midas.scripts import MDJob
from midas import RankEntry
from midas.tools import group_by_key
from midas.tools import get_key
from midas.tools import split_key_value

logger = logging.getLogger(__name__)


class AlexaToNamesAndOne(MDJob):
    """ Parse Alexa Top1M files and print the names found in the
    entries as key and a `1' as value.
    """

    def run(self):
        for fname in self.args.stream:
            logger.info("processing '{0}'".format(fname))
            for entry in RankEntry.iter_alexa_file(fname):
                print("{0}\t1".format(entry.site))


class SumValues(MDJob):
    """ Sums up the counts of the keys.
    """

    def run(self):
        for group in group_by_key(self.args.stream, get_key):
            counter = 0
            for name_tab_count in group:
                name, count = split_key_value(name_tab_count)
                counter += int(count)
            print('{0}\t{1}'.format(name, counter))
