# -*- coding: utf-8 -*-

import glob
import os.path

import midas.compat as vt_comp

import midas as md
import midas.config as md_cfg
import midas.scripts as md_scripts

class IndexDates(md_scripts.MDCommand):

    def add_argument(self):
        self.parser.add_argument(
            'dir', nargs='?', metavar='DIR',
            default=md_cfg.get('location', 'alexa_files'),
            help='The directory where the Alexa Top1M files can be found'
            )


    def run(self):
        files = glob.glob(os.path.join(self.args.dir, 'top_1m_????-??-??.gz'))
        dates = sorted(md.parse_tstamp(fname, 'top_1m_%Y-%m-%d.gz')
                       for fname in vt_comp.imap(os.path.basename, files))
        with vt_comp.GzipFile(md_cfg.get('location', 'dates_file'), 'w') as fp:
            fp.writelines('{0}\n'.format(date.strftime(md.TS_FORMAT)).encode()
                          for date in dates)
