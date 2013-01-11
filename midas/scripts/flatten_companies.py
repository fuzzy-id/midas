#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import json
import sys

from midas.scripts import MDCommand

FR_OF_INTEREST = set(['seed', 'angel', 'a'])

class FlattenCompanies(MDCommand):

    def run(self):
        for js in self.stdin:
            d = json.loads(js)
            permalink = d['permalink']
            hp = d.get('homepage_url', '')
            if hp is None:
                hp = ''
            fundings = []
            for fr in d.get('funding_rounds', []):
                if (fr['round_code'] in FR_OF_INTEREST
                    and fr['funded_year']
                    and fr['funded_month'] 
                    and fr['funded_day']
                    and fr['funded_year'] > 1900):  # Required by strftime
                    funding = (datetime.date(fr['funded_year'],
                                             fr['funded_month'],
                                             fr['funded_day']), 
                               fr['round_code'])
                    fundings.append(funding)
            if len(fundings) > 0:
                tstamp, code = max(fundings)
                funding = '\t'.join((code, tstamp.strftime('%Y-%m-%d')))
            else:
                funding = ''
            try:
                self.out('\t'.join((permalink, hp, funding)))
            except:
                print(permalink, file=sys.stderr)
                print(hp, file=sys.stderr)
                print(funding, file=sys.stderr)
                raise
