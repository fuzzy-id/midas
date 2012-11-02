# -*- coding: utf-8 -*-

import logging

import mrjob.job as mr_job

from midas.scripts import MDJob
from midas import RankEntry
from midas.tools import group_by_key
from midas.tools import get_key
from midas.tools import split_key_value

logger = logging.getLogger(__name__)

class AlexaCountSitesJob(mr_job.MRJob):

    def mapper(self, key, fname):
        """ Parse Alexa Top1M files and print the names found in the
        entries as key and a `1' as value.
        """
        logger.info("processing '{0}'".format(fname))
        for entry in RankEntry.iter_alexa_file(fname):
            yield entry.site, 1

    def reducer(self, site, occurences):
        """ Sums up the counts of the sites.
        """
        yield site, sum(occurences)
