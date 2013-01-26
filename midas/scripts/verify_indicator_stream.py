# -*- coding: utf-8 -*-

import struct

import bitarray

from midas.scripts import MDCommand

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

def to_string(site, features):
    return '{0}\t{{{1}}}'.format(
        site, ','.join( 
            '({0},({1}))'.format(
                tstamp, ','.join(map(str, vectors.tolist())) 
                )
                for tstamp, vectors in features 
            )
        )

class VerifyIndicatorStream(MDCommand):
    """
    Converts a file of `stream-alexa-indicators' to something
    Pig-parseable.
    """

    def add_argument(self):
        self.parser.add_argument('num_features', type=int,
                                 help='The number of features per vector')
        self.parser.add_argument('istream', metavar='FILE', 
                                 help='The binary istream-file')
        
    def run(self):
        with open(self.args.istream, 'rb') as fp:
            for site_id, features in iter_features(fp, self.args.num_features):
                self.out(to_string(site_id, features))
