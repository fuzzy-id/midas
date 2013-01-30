# -*- coding: utf-8 -*-

import argparse
import datetime
import itertools
import queue
import threading
import struct
import subprocess
import sys

import bitarray
import lazy
import numpy
import yaml

from midas import parse_tstamp
from midas.compat import d_iteritems
from midas.compat import d_itervalues
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

    @lazy.lazy
    def fname(self):
        return os.path.join(self.cache_dir, 
                            '_'.join(map(str, [self.name,
                                               self.ndays,
                                               self.threshold])))

    @property
    def produced(self):
        return os.path.isfile(self.fname)

    def update(self, indicators):
        self._cache = dict()
        with open(self.fname, 'w', newline='') as fp:
            writer = csv.writer(fp)
            for site, indicator in indicators:
                writer.writerow([site, indicator])
                self._cache[site] = indicator
            
    @lazy.lazy
    def data(self):
        d = dict()
        with open(self.fname, newline='') as fp:
            reader = csv.reader(fp):
            for site, bool_ in reader:
                if bool_ == 'True':
                    bool_ = True
                else:
                    bool_ = False
                d[site] = bool_
        return d


class IndicatorUpdater(threading.Thread):

    def __init__(self, ids_to_samples, to_produce_q, caller):
        self.ids_to_samples = ids_to_samples
        self.to_produce_q = to_produce_q
        self.caller = caller

    def run(self):
        while True:
            try:
                indicator = self.to_produce_q.get(block=False)
            except queue.Empty:
                break
            data = list()
            for site_id, features in self.caller.call(indicator):
                site, tstamp, code = self.ids_to_samples[site_id]
                for secs, bool_ in features:
                    feat_tstamp = datetime.datetime.fromtimestamp(secs)
                    if tstamp < feat_tstamp:
                        data.append(site, last_indicator)
                        break
                    last_indicator = bool_[0]
            indicator.update(data)
            self.to_produce_q.task_done()

class StreamAlexaIndicatorsCaller(object):

    def __init__(self, cmd, arguments=['--dbpivot', ], num_features=1):
        self.cmd = cmd
        self.arguments = arguments
        self.num_features = num_features

    def call(self, indicator):
        cmd = [self.cmd, ] + self.arguments + [ str(indicator) ]
        subp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for features in iter_features(subp.stdout, self.num_features):
            yield features
        if subp.poll() != 0:  # pragma: no cover
            raise Exception(
                'Subprocess did not succeed: {0}'.format(subp.returncode)
                )

class MakeAlexaIndicators(MDCommand):
    """
    Run `stream-alexa-indicators`.

    The arguments can either be given via the YAML config file or the
    command-line. If an argument is provided in both ways the
    command-line takes precedence.
    """

    classes=['seed', 'angel', 'a', 'negative']

    def add_argument(self):
        self.parser.add_argument(
            '--exec',
            help="The path to the `stream-alexa-indicators' command"
            )
        self.parser.add_argument(
            '--num_threads', type=int,
            help="How many threads shall work in parallel"
            )
        self.parser.add_argument(
            '--indicators_cache', type=CheckDirectoryAction,
            help=" ".join(["The directory where indicator files",
                           "should be cached. The default is the",
                           "dirname of the `config'-file."])
            )
        self.parser.add_argument(
            '--ids_to_sites',
            help="File providing the mapping site_id <-> site"
            )
        self.parser.add_argument(
            '--samples', type=StoreSingleFileOrDirectoryAction,
            help="Directory containing the samples"
            )
        self.parser.add_argument(
            'config',
            help='YAML-file containing the wanted features')

    @lazy.lazy
    def config(self):
        with open(self.args.config) as fp:
            config = yaml.safe_load(fp.read())
        return config

    @lazy.lazy
    def cmd_path(self):
        if self.args.exec:
            return self.args.exec
        return self.config['exec']

    @lazy.lazy
    def sites_to_ids(self):
        if self.args.ids_to_sites:
            f = self.args.ids_to_sites
        else:
            f = self.args.config['ids_to_sites']
        with open(f, newline='') as fp:
            sites_to_ids = dict(
                (site, int(site_id))
                for site_id, site in csv.reader(fp, delimiter='\t')
                )
        return sites_to_ids

    @lazy.lazy
    def ids_to_samples(self):
        if self.args.samples:
            f = self.args.samples
        else:
            f = self.args.config['samples']
        with open(f, newline='') as fp:
            samples = dict()
            for site, tstamp, code in csv.reader(fp, delimiter='\t'):
                tstamp = parse_tstamp(tstamp)
                site_id = sites_to_ids[site]
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
            ndays = args['ndays']
            thresholds = args['thresholds']
            if isinstance(ndays, dict):
                ndays = numpy.arange(ndays['start'], 
                                     ndays['stop'], 
                                     ndays.get('step', 1))
            if isinstance(thresholds, dict):
                thresholds = numpy.arange(thresholds['start'], 
                                          thresholds['stop'], 
                                          thresholds.get('step', 1))
            for days, threshold in itertools.product(ndays, thresholds):
                indicators.append(Indicator(filter_, 
                                            days,
                                            threshold, 
                                            self.cache_dir))
        return indicators

    def run(self):
        to_produce_q = queue.Queue()
        for i in self.indicators:
            if not i.produced():
                to_produce_q.put(i)
        for _ in range(min(self.num_threads, to_produce_q.qsize())):
            t = GetIndicator(self.indicators_cache,
                             self.ids_to_samples, 
                             to_produce_q,
                             StreamAlexaIndicatorsCaller(self.cache_dir))
            t.daemon = True
            t.start()
        indicators_q.join()
        features = dict()
        for site, tstamp, code in d_itervalues(self.ids_to_samples):
            features[site] = [code, ]
            for indicator in self.indicators:
                features[site].append(indicator[site])

        root, _ = os.path.splitext(self.args.config)
        data_f = '.'.join([root, 'data'])
        names_f = '.'.join([root, 'names'])
        with open(data_f, 'w', newline='') as fp:
            writer = csv.writer(fp)
            for site_id, features in site_id_to_indicator:
                site, tstamp, code = self.ids_to_sample[site_id]
                row = [site, code]
                row.extend(features)
                writer.writerow(row)
        with open(names_f, 'w') as fp:
            fp.write(self.names)

    @lazy.lazy
    def names(self):
        s = NAMES_TPL.format(
            ', '.join(self.classes),
            '\n'.join('{0}_{1}_{2}:\tTrue, False.'.format(i.name,
                                                          i.ndays,
                                                          i.threshold)
                      for t in self.indicators)
            )
        return s
