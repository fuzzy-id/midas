# -*- coding: utf-8 -*-

from __future__ import print_function

import glob
import os.path

from midas.compat import ZipFile

import midas
import midas.scripts as md_scripts

ALEXA_ZIP_FILE_FORMAT='top-1m-????-??-??.csv.zip'
#: The time-stamp format as encoded in Alexa's Top1M files.
ALEXA_TS_FORMAT='top-1m-%Y-%m-%d.csv.zip'

class UnzipAlexaFiles(md_scripts.MDCommand):
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
            help='The directory to put the unzipped files'
            )

    def run(self):
        src, dst = self.args.src[0], self.args.dst[0]
        zip_files = glob.glob(
            os.path.join(src, ALEXA_ZIP_FILE_FORMAT)
            )
        zip_files.sort()
        for zip_f in zip_files:
            basename = os.path.basename(zip_f)
            date = midas.parse_tstamp(basename, ALEXA_TS_FORMAT)
            tstamp = midas.serialize_tstamp(date)
            dst_fname = 'top_1m_{0}'.format(tstamp)
            dst_f = os.path.join(dst, dst_fname)
            if os.path.isfile(dst_f):
                self.out('Skipping {0}'.format(basename))
            else:
                with open(dst_f, 'w') as fp:
                    for site, rank in iter_alexa_file(zip_f):
                        fp.write('{0},{1},{2}\n'.format(site, tstamp, rank))
                self.out('Processed {0}'.format(basename))


def iter_alexa_file(fname):
    """ Returns an iterator yielding a :class:`RankEntry` for
    every line it finds in the file in the archive `fname`.

    The standard Alexa Top1M data is a :class:`zipfile.ZipFile`. The
    archive contains one file named `top-1m.csv`. The lines in this
    file have the form `rank,site` (no spaces!).

    As the time-stamp is encoded in the file name (defined by
    :attr:`ALEXA_TS_FORMAT`) and not in the line, parsing cannot be
    done line-by-line but needs to be done on a per file basis.
    """
    with ZipFile(fname) as zf:
        # The archive contains one file named ``top-1m.csv``
        for line in zf.open('top-1m.csv'):
            rank, name = line.decode().strip().split(',', 1)
            yield (name, rank)
