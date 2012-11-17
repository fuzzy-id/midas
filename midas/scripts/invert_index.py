# -*- coding: utf-8 -*-

import mrjob.job as mr_job

class InvertIndex(mr_job.MRJob):

    def mapper(self, key, value):
        return value['site'], (value['tstamp'], value['rank'])
