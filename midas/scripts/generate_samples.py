# -*- coding: utf-8 -*-
import collections
import shelve
import random
import sys

import pandas

from midas.scripts import MDCommand
from midas.pig_schema import make_parser
from midas.pig_schema import make_serializer
from midas.pig_schema import pig_schema_to_py_struct

PARSER = make_parser(
    pig_schema_to_py_struct(
        '(site:chararray, ranking: bag{(tstamp:chararray, rank:int)})'
        )
    )

class GenerateSamples(MDCommand):
    """ 
    This script ideally creates one sample for each company with an
    associated sites that has restrictions stored in the
    shelve. Hence, you first have to merge/split the original files
    containing the data (this should be `sites_wo_company`) into the
    right amount of splits, e.g. if your data is located in files
    /data/sites_wo_company/part-*

    DATA=/data/sites_wo_company/part-*
    split_size=$(( $(cat ${DATA} | wc -l) / 10 + 1))
    cat ${DATA} | split -l ${split_size} - splitted_

    This will generate files with the naming scheme `splitted_aa`,
    `splitted_ab`, etc. in your current working directory. Now start
    this very script once per file:

    for f in /path/to/splitted_*; do \\
      out=/data/results/result_$(basename ${f}) \\
      cat ${f} | ./generate_samples.py restrictions_shelve > ${out} & \\
    done
    """

    def add_argument(self):
        self.parser.add_argument(
            'shelf', help='The file-name of the restrictions shelf.'
            )

    def run(self):
        shelf = shelve.open(self.args.shelf)
        restrictions = shelf.items()
        random.shuffle(restrictions)
        for line in self._in:
            if len(restrictions) > 0:
                data = PARSER(line)
                series = pandas.Series(dict((pandas.Timestamp(d), r)
                                            for d, r in data.ranking))
                for i, (company, restriction) in enumerate(restrictions):
                    if restriction.fulfills(series):
                        restrictions.pop(i)
                        self.out('\t'.join(
                                [data.site, 
                                 restriction.tstamp.date().isoformat()]
                                ))
        shelf.close()
