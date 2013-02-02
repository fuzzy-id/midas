# -*- coding: utf-8 -*-

import argparse
import copy
import datetime
import functools
import itertools
import os
import os.path
import operator
import threading
import struct
import subprocess
import sys

import bitarray
import lazy
import numpy
import yaml

from midas import parse_tstamp
from midas.compat import QueueEmpty
from midas.compat import Queue
from midas.compat import csv_file_reader
from midas.compat import csv_file_writer
from midas.compat import d_iteritems
from midas.compat import d_itervalues
from midas.compat import imap
from midas.scripts import CheckDirectoryAction
from midas.scripts import MDCommand
from midas.scripts import StoreSingleFileOrDirectoryAction


FILTERS = set(['rsi', 'ols-slope', 'spearman', 'pearson', 'rank'])

FMT_u32="I"

NAMES_TPL="""class.

site:\tlabel.
class:\t{0}.
{1}
"""


def interpret_next_bits(fp, fmt=FMT_u32):
    buf = fp.read(struct.calcsize(fmt))
    if not buf:
        return None
    return struct.unpack(fmt, buf)[0]

def iter_features(fp, num_features):
    bitarraysize = int((num_features + 7) / 8)
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
        self.parser.add_argument('istream', metavar='FILE', nargs='?', 
                                 default=sys.stdin,
                                 help='The binary istream-file')
        
    def run(self):
        with open(self.args.istream, 'rb') as fp:
            for site_id, features in iter_features(fp, self.args.num_features):
                self.out(to_string(site_id, features))


class Indicator(object):

    def __init__(self, name, ndays, threshold, cache_dir):
        self.name = name
        self.ndays = ndays
        self.threshold = threshold
        self.cache_dir = cache_dir

    def __str__(self):
        if self.name == 'rank':
            return '{0}_{1}'.format(self.name, self.threshold)
        return '{0}_{1}_{2:.2f}'.format(self.name, 
                                        self.ndays,
                                        self.threshold)

    @lazy.lazy
    def cmd_argument(self):
        if self.name == 'rank':
            return '{i.name},{i.threshold}'.format(i=self)
        return '{i.name},{i.ndays},{i.threshold:.2f}'.format(i=self)


    @lazy.lazy
    def fname(self):
        return os.path.join(self.cache_dir, str(self))

    @property
    def produced(self):
        return os.path.isfile(self.fname)

    def update(self, indicators):
        self._cache = dict()
        with csv_file_writer(self.fname) as writer:
            for site, indicator in indicators:
                writer.writerow([site, indicator])
                self._cache[site] = indicator
            
    @lazy.lazy
    def data(self):
        d = dict()
        for site, bool_ in csv_file_reader(self.fname):
            if bool_ == 'True':
                bool_ = True
            else:
                bool_ = False
            d[site] = bool_
        return d


class IndicatorUpdater(threading.Thread):

    def __init__(self, ids_to_samples, to_produce_q, caller):
        threading.Thread.__init__(self)
        self.ids_to_samples = ids_to_samples
        self.to_produce_q = to_produce_q
        self.caller = caller
        self.failed = False

    def run(self):
        while True:
            try:
                indicator = self.to_produce_q.get(block=False)
                data = list()
                for site_id, features in self.caller.call(indicator):
                    if site_id not in self.ids_to_samples:
                        continue
                    site, tstamp, code = self.ids_to_samples[site_id]
                    for secs, bool_ in features:
                        feat_tstamp = datetime.datetime.fromtimestamp(secs)
                        if tstamp < feat_tstamp:
                            break
                        last_indicator = bool_[0]
                    data.append((site, last_indicator))
                indicator.update(data)
                self.to_produce_q.task_done()
            except QueueEmpty:
                break
            except:
                self.failed = True
                self.to_produce_q.task_done()
                raise

class StreamAlexaIndicatorsCaller(object):

    def __init__(self, cmd, arguments=['--dbpivot', ], num_features=1):
        self.cmd = cmd
        self.arguments = arguments
        self.num_features = num_features

    def call(self, indicator):
        args = [self.cmd, ]
        args.extend(self.arguments)
        args.append(indicator.cmd_argument)
        subp = subprocess.Popen(args, stdout=subprocess.PIPE)
        for features in iter_features(subp.stdout, self.num_features):
            yield features
        if subp.wait() != 0:  # pragma: no cover
            raise Exception(
                'Subprocess did not succeed: {0}'.format(subp.returncode)
                )

class CreateFeatures(MDCommand):
    """
    Run `stream-alexa-indicators`.

    The arguments can either be given via the YAML config file or the
    command-line. If an argument is provided in both ways the
    command-line takes precedence.
    """

    classes=['seed', 'angel', 'a', 'negative']

    def add_argument(self):
        self.parser.add_argument(
            '--executable',
            help="The path to the `stream-alexa-indicators' command"
            )
        self.parser.add_argument(
            '--num_threads', type=int,
            help="How many threads shall work in parallel"
            )
        self.parser.add_argument(
            '--indicators_cache',
            help=" ".join(["The directory where indicator files",
                           "should be cached."])
            )
        self.parser.add_argument(
            '--ids_to_sites',
            help="File providing the mapping site_id <-> site"
            )
        self.parser.add_argument(
            '--samples',
            help="Directory containing the samples"
            )
        self.parser.add_argument(
            'config',
            help='YAML-file containing the wanted features')

    @lazy.lazy
    def num_threads(self):
        if self.args.num_threads:
            return self.args.num_threads
        return self.config['num_threads']

    @lazy.lazy
    def config(self):
        with open(self.args.config) as fp:
            config = yaml.safe_load(fp.read())
        return config

    @lazy.lazy
    def cmd_path(self):
        if self.args.executable:
            return self.args.executable
        return self.config['executable']

    @lazy.lazy
    def sites_to_ids(self):
        if self.args.ids_to_sites:
            f = self.args.ids_to_sites
        else:
            f = self.config['ids_to_sites']
        sites_to_ids = dict()
        for site_id, site in csv_file_reader(f, delimiter='\t'):
            sites_to_ids[site] = int(site_id)
        return sites_to_ids

    @lazy.lazy
    def ids_to_samples(self):
        if self.args.samples:
            directory = self.args.samples
        else:
            directory = self.config['samples']
        if os.path.isfile(directory):
            files = [directory, ]
        else:
            files = []
            make_abs = functools.partial(os.path.join, directory)
            for path in imap(make_abs, os.listdir(directory)):
                if os.path.isfile(path):
                    files.append(path)
        samples = dict()
        for f in files:
            for site, tstamp, code in csv_file_reader(f, delimiter='\t'):
                tstamp = parse_tstamp(tstamp)
                site_id = self.sites_to_ids[site]
                samples[site_id] = (site, tstamp, code)
        return samples

    @lazy.lazy
    def indicators_cache(self):
        if self.args.indicators_cache:
            return self.args.indicators_cache
        return self.config['indicators_cache']

    @lazy.lazy
    def indicators(self):
        indicators = list()
        for filter_ in FILTERS:
            if not filter_ in self.config:
                continue
            args = self.config[filter_]
            if filter_ != 'rank':
                ndays = args['ndays']
                if isinstance(ndays, dict):
                    ndays = numpy.arange(ndays['start'], 
                                         ndays['stop'], 
                                         ndays.get('step', 1))
            else:
                ndays = [None, ]
            thresholds = args['thresholds']
            if isinstance(thresholds, dict):
                thresholds = numpy.arange(thresholds['start'], 
                                          thresholds['stop'], 
                                          thresholds.get('step', 1))
            for days, threshold in itertools.product(ndays, thresholds):
                indicators.append(Indicator(filter_, 
                                            days,
                                            threshold, 
                                            self.indicators_cache))
        return indicators

    def run(self):
        to_produce_q = Queue()
        for i in self.indicators:
            if not i.produced:
                to_produce_q.put(i)
        threads = []
        for _ in range(min(self.num_threads, to_produce_q.qsize())):
            t = IndicatorUpdater(self.ids_to_samples, 
                                 to_produce_q,
                                 StreamAlexaIndicatorsCaller(self.cmd_path))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        if any(imap(operator.attrgetter('failed'), threads)):
            raise Exception('At least one thread died!')
        to_produce_q.join()
        features = dict()
        for site, tstamp, code in d_itervalues(self.ids_to_samples):
            features[site] = list()
            for indicator in self.indicators:
                try:
                    feature = indicator.data[site]
                except KeyError:
                    self.out(
                        'Could not find {0} in indicators stream'.format(site)
                        )
                else:
                    features[site].append(feature)

        root, _ = os.path.splitext(self.args.config)
        data_f = '.'.join([root, 'data'])
        names_f = '.'.join([root, 'names'])
        with csv_file_writer(data_f) as writer:
            for site, tstamp, code in d_itervalues(self.ids_to_samples):
                if len(features[site]) == len(self.indicators):
                    row = [site, code]
                    row.extend(features[site])
                    writer.writerow(row)
        with open(names_f, 'w') as fp:
            fp.write(self.names)

    @lazy.lazy
    def names(self):
        s = NAMES_TPL.format(
            ', '.join(self.classes),
            '\n'.join('{0}:\tTrue, False.'.format(str(i))
                      for i in self.indicators)
            )
        return s
