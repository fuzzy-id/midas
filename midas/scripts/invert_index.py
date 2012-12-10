# -*- coding: utf-8 -*-

import mrjob.job as mr_job
import mrjob.protocol as mr_prot

class InvertIndex(mr_job.MRJob):

    INPUT_PROTOCOL = mr_prot.JSONValueProtocol

    def mapper(self, _, rank_json):
        yield rank_json['site'], (rank_json['tstamp'], rank_json['rank'])

    def reducer(self, site, tstamp_ranks):
        yield (site, sorted(tstamp_ranks))

if __name__ == '__main__':  # pragma: no cover
    InvertIndex.run()
