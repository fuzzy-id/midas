# -*- coding: utf-8 -*-

from __future__ import print_function

import itertools
import glob
import os.path

import vincetools.compat as vt_comp

import midas
import midas.scripts as md_scripts

class AlexaZipToGzip(md_scripts.MDCommand):
    """ Unzip Alexa Top 1M ZIP files and put the content in gzip
    files. The content is copied as is. The 'csv.zip' extension of the
    file is replaced by 'gz'.
    """

    def add_argument(self):
        self.parser.add_argument(
            'src', nargs=1, metavar='SOURCE',
            help='The directory where ZIP files can be found'
            )
        self.parser.add_argument(
            'dst', nargs=1, metavar='DEST',
            help='The directory to put the gzip files'
            )

    def run(self):
        zip_files = glob.glob(
            os.path.join(self.args.src[0], 'top-1m-????-??-??.csv.zip')
            )
        zip_files.sort()
        for zip_f in zip_files:
            print('Processing {0}'.format(zip_f), end=' ', file=self.out)
            f_iter = midas.RankEntry.iter_alexa_file(zip_f)
            first_entry = next(f_iter)
            gz_fname = 'top_1m_{0}.gz'.format(first_entry.tstamp)
            gz_f = os.path.join(self.args.dst[0], gz_fname)
            if os.path.isfile(gz_f):
                print('SKIP', file=self.out)
            else:
                print('-> {0}'.format(gz_f), end=' ', file=self.out)
                with vt_comp.GzipFile(gz_f, 'w') as fp:
                    fp.writelines(
                        ''.join((entry.format_json, '\n')).encode('utf-8')
                        for entry in itertools.chain([first_entry], f_iter)
                        )
                print('DONE', file=self.out)
