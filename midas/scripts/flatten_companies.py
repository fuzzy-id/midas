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
            if d.get('homepage_url'):
                hp = d['homepage_url']
            else:
                hp = ''
            if d.get('funding_rounds') and len(d['funding_rounds']) > 0:
                try:
                    fundings = []
                    for fr in d['funding_rounds']:
                        if fr['round_code'] in FR_OF_INTEREST:
                            if (fr['funded_year'] and fr['funded_month'] and fr['funded_day']
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
                except:
                    print(d['funding_rounds'], file=sys.stderr)
                    print(d, file=sys.stderr)
                    raise
            else:
                funding = ''

            self.out('\t'.join((permalink, hp, funding)))
