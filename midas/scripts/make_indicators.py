# -*- coding: utf-8 -*-

import argparse
import itertools
import queue
import threading
import subprocess

import numpy
import yaml

from midas import parse_tstamp
from midas.compat import d_iteritems
from midas.scripts import CheckDirectoryAction
from midas.scripts import MDCommand
from midas.scripts import StoreSingleFileOrDirectoryAction
from midas.scripts.verify_indicator_stream import iter_features
from midas.scripts.verify_indicator_stream import to_string

FILTERS = set(['rsi', 'ols-slope', 'spearman', 'pearson', 'rank'])

def expand_config(conf):
    for filter_ in FILTERS:
        if not filter_ in conf:
            continue
        args = conf[filter_]
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
            yield (filter_, days, threshold)
            
class GetIndicator(threading.Thread):

    def __init__(self, cache_path, ids_to_samples, indicators_q, features_q):
        self.cache_path = cache_path
        self.ids_to_samples = ids_to_samples
        self.indicators_q = indicators_q
        self.features_q = features_q

    def run(self):
        while True:
            try:
                feature = self.indicators_q.get(block=False)
            except queue.Empty:
                break
            feature_name = '_'.join(feature)
            feature_file = os.path.join(self.cache_path, feature_name)
            site_id_to_indicator = dict()
            if os.path.isfile(feature_file):
                with open(feature_file, newline='') as fp:
                    reader = csv.reader(fp)
                    for site_id, indicator in reader:
                        site_id = int(site_id)
                        if indicator == 'True':
                            indicator = True
                        else:
                            indicator = False


def call_stream_alexa_indicators(conf):
    cmd = [conf['exec'], '--dbpivot']
    num_features = 0
    for args in expand_config(conf):
        cmd.append(','.join(map(str, args)))
        num_features += 1
    subp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for features in iter_features(subp.stdout, num_features):
        yield features
    if subp.poll() != 0:  # pragma: no cover
        raise Exception('Subprocess did not succeed: {0}'.format(subp.returncode))

class MakeAlexaIndicators(MDCommand):
    """
    Run `stream-alexa-indicators`.
    """

    def add_argument(self):
        self.parser.add_argument(
            '--num_threads', '-t',
            help="How many threads shall work in parallel"
            )
        self.parser.add_argument(
            '--indicators_cache', '-i', type=CheckDirectoryAction,
            help=" ".join(["The directory where indicator files",
                           "should be cached. The default is the",
                           "dirname of the `config'-file."])
            )
        self.parser.add_argument(
            'ids_to_sites',
            help="File providing the mapping site_id <-> site"
            )
        self.parser.add_argument(
            'samples', type=StoreSingleFileOrDirectoryAction,
            help="Directory containing the samples"
            )
        self.parser.add_argument(
            'config',
            help='YAML-file containing the wanted features')

    def run(self):
        self.process_arguments()
        indicators_q = queue.Queue()
        for i in self.indicators:
            q.put(i)
        features_q = queue.Queue()
        for _ in range(self.args.num_threads):
            t = GetIndicator(self.args.indicators_cache,
                             self.ids_to_sample, 
                             indicators_q,
                             features_q)
            t.daemon = True
            t.start()
        indicators_q.join()
        features = collections.defaultdict(list)
        self.names = list()
        while not features_q.empty():
            feature, site_id_to_indicator = features_q.get()
            self.names.append(feature)
            for site_id, indicator in site_id_to_indicator:
                features[site_id].append(indicator)
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
            self.generate_names(fp)

    def generate_names(self, fp, classes=['seed', 'angel', 'a', 'negative']):
        tpl = """
class.

site:\tlabel.
class:\t{0}.
{1}
"""
        s = tpl.format(', '.join(classes),
                       '\n'.join('{0}_{1}_{2}:\tTrue, False.'.format(*t)
                                 for t in self.names))
        fp.write(s)

    def process_arguments(self):
        with open(self.args.config) as fp:
            self.indicators = expand_config(yaml.safe_load(fp.read()))
        with open(self.args.ids_to_sites, newline='') as csv_fp:
            sites_to_ids = dict(
                (site, int(site_id))
                for site_id, site in csv.reader(csv_fp, delimiter='\t')
                )
        with open(self.args.samples, newline='') as csv_fp:
            self.ids_to_sample = dict()
            for site, tstamp, code in csv.reader(csv_fp, delimiter='\t'):
                tstamp = parse_tstamp(tstamp)
                site_id = sites_to_ids[site]
                self.ids_to_sample[site_id] = (site, tstamp, code)
        if self.args.indicators_cache is None:
            self.args.indicators_cache = os.path.dirname(self.args.config)
