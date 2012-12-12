#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import json
import sys

def prepare(data):
    for js in data:
        d = json.loads(js)
        permalink = d['permalink']
        if d.get('homepage_url'):
            hp = d['homepage_url']
        else:
            hp = ''
        if len(d.get('funding_rounds', [])) > 0:
            funding = max((datetime.date(fr['funded_year'],
                                         fr['funded_month'], 
                                         fr['funded_day']), fr['round_code'])
                          for fr in d.get('funding_rounds', []))
            funding = '\t'.join((funding[1], funding[0].strftime('%Y-%m-%d')))
        else:
            funding = ''
        
        print('\t'.join((permalink, hp, funding)))

if __name__ == '__main__':
    prepare(sys.stdin)
