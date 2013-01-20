# -*- coding: utf-8 -*-
import argparse
import sys
import struct
import pprint

import bitarray

FMT_u32="I"

def interpret_next_bits(fp, fmt=FMT_u32):
    buf = fp.read(struct.calcsize(fmt))
    if not buf:
        return None
    return struct.unpack(fmt, buf)[0]

def iter_features(fp, num_features):
    bitarraysize = (num_features + 7) / 8
    while True:
        site_id = interpret_next_bits(fp)
        if not site_id:
            break
        features = []
        while True:
            tstamp = interpret_next_bits(fp)
            if tstamp == 0:
                break
            bits = bitarray.bitarray(endian='little')
            bits.frombytes(fp.read(bitarraysize))
            features.append((tstamp, bits[:num_features]))
        yield (site_id, features)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('num_features', type=int,
                           help='The number of features per vector')
    argparser.add_argument('istream', metavar='FILE', 
                           help='The binary istream-file')
    args = argparser.parse_args(sys.argv[1:])
    with open(args.istream, 'rb') as fp:
        for site_id, features in iter_features(fp, args.num_features):
            pprint.pprint((site_id, features))

if __name__ == "__main__":
    main()
