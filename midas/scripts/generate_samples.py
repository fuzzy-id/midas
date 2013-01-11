#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script ideally creates one sample for each company with an
associated sites that has restrictions stored in the shelve. Hence,
you first have to merge/split the original files containing the data
(this should be `sites_wo_company`) into the right amount of splits,
e.g. if your data is located in files /data/sites_wo_company/part-*

DATA=/data/sites_wo_company/part-*
split_size=$(( $(cat ${DATA} | wc -l) / 10 + 1)); cat ${DATA} | split -l ${split_size} - splitted_

This will generate files with the naming scheme `splitted_aa`,
`splitted_ab`, etc. in your current working directory. Now start this
very script once per file:

for f in /path/to/splitted_*; do out=/data/results/result_$(basename ${f}); cat ${f} | ./generate_samples.py > ${out} & done
"""

import collections
import shelve
import random
import restrictions
import sys

import pandas

import pig_schema

SHELVE_FILE = 'restrictions_shelve'

OUT_TUPLE = collections.namedtuple('Tuple', 'site company tstamp')

@pig_schema.pig_output(
    '(site:chararray, company: chararray, tstamp: chararray)'
    )
@pig_schema.pig_input(
    '(site:chararray, ranking: bag{(tstamp:chararray, rank:int)})'
    )
def main(field):
    if len(RESTRICTIONS) > 0:
        series = pandas.Series(dict((pandas.Timestamp(d), r)
                                    for d, r in field.ranking))
        for i, (company, restriction) in enumerate(RESTRICTIONS):
            if restriction.fulfills(series):
                RESTRICTIONS.pop(i)
                out = OUT_TUPLE(field.site, 
                                company, 
                                restriction.tstamp.date().isoformat())
                yield out
                break

if __name__ == '__main__':
    SHELF = shelve.open(SHELVE_FILE)
    RESTRICTIONS = SHELF.items()
    random.shuffle(RESTRICTIONS)
    SHELF.close()
    main(sys.stdin)
