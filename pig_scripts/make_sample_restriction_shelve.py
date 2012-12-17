#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve

import pandas

import pig_schema

@pig_schema.pig_input(','.join(['(site: chararray',
                                'ranking: bag{(tstamp: chararray, rank: int)}',
                                'company: chararray',
                                'code: chararray',
                                'tstamp: chararray)']))
def main(field):
    print(repr(field))
    

if __name__ == '__main__':
    main(sys.stdin)
