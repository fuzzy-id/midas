#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import json

def prepare(data):
    for js in data:
        d = json.loads(js)
        permalink = d['permalink']
        if d.get('homepage_url'):
            hp = d['homepage_url']
        else:
            hp = ''
        funding = max((datetime.date(fr['funded_year'],
                                     fr['funded_month'], 
                                     fr['funded_day']), fr['round_code'])
                      for fr in d.get('funding_rounds', []))
        
        print('\t'.join([permalink, hp, 
                         funding[0].strftime('%Y-%m-%d'), funding[1]]))
        

if __name__ == '__main__':
    prepare(sys.stdin)
