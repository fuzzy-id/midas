# -*- coding: utf-8 -*-

import argparse
import itertools
import subprocess

import yaml

from midas.compat import d_iteritems
from midas.scripts import MDCommand
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
            ndays = xrange(ndays['start'], 
                           ndays['stop'], 
                           ndays.get('step', 1))
        if isinstance(thresholds, dict):
            thresholds = xrange(thresholds['start'], 
                                thresholds['stop'], 
                                thresholds.get('step', 1))
        for days, threshold in itertools.product(ndays, thresholds):
            yield (filter_, days, threshold)
            

def generate_names(conf, classes=['seed', 'angel', 'a', 'negative']):
    tpl = """
class.

site:\tlabel.
class:\t{0}.
{1}
"""
    return tpl.format(', '.join(classes),
                      '\n'.join('{0}_{1}_{2}:\tTrue, False.'.format(*t)
                                for t in expand_config(conf)))

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
        self.parser.add_argument('names_file', type=argparse.FileType('w'),
                                 help="The `.names' file that shall be written")
        self.parser.add_argument('indicators_file', type=argparse.FileType('w'),
                                 help="The indicators file that shall be written")
        self.parser.add_argument('yaml_file', type=argparse.FileType(),
                                 help='Parameters-file to run `stream-alexa-indicators`')

    def run(self):
        conf = yaml.safe_load(self.args.yaml_file)
        for site_id, features in call_stream_alexa_indicators(conf):
            self.args.indicators_file.write(to_string(site_id, features))
            self.args.indicators_file.write('\n')
        self.args.names_file.write(generate_names(conf))
