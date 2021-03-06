# -*- coding: utf-8 -*-

import glob
import os.path

from midas.compat import ZipFile

import midas
import midas.scripts

ALEXA_ZIP_FILE_FORMAT='top-1m-????-??-??.csv.zip'
#: The time-stamp format as encoded in Alexa's Top1M files.
ALEXA_TS_FORMAT='top-1m-%Y-%m-%d.csv.zip'

class UnzipAlexaFiles(midas.scripts.MDCommand):
    """ 
    Unzip Alexa Top 1M ZIP files and put the content in tab ('\t')
    separated files. The content is copied as is. The 'csv.zip'
    extension of the file is omitted.
    """

    def add_argument(self):
        self.parser.add_argument('src', metavar='SOURCE',
                                 action=midas.scripts.CheckDirectoryAction,
                                 help='The directory where ZIP files can be found')
        self.parser.add_argument('dst', metavar='DEST',
                                 action=midas.scripts.CheckDirectoryAction,
                                 help='The directory to put the unzipped files')

    def run(self):
        zip_files = glob.glob(os.path.join(self.args.src, 
                                           ALEXA_ZIP_FILE_FORMAT))
        zip_files.sort()
        for zip_f in zip_files:
            basename = os.path.basename(zip_f)
            date = midas.parse_tstamp(basename, ALEXA_TS_FORMAT)
            tstamp = midas.serialize_tstamp(date)
            dst_fname = 'top_1m_{0}'.format(tstamp)
            dst_f = os.path.join(self.args.dst, dst_fname)
            if os.path.isfile(dst_f) or os.stat(zip_f).st_size == 0:
                self.out('Skipping {0}'.format(basename))
            else:
                with open(dst_f, 'w') as fp:
                    for site, rank in iter_alexa_zip_file(zip_f):
                        fp.write('{0}\t{1}\t{2}\n'.format(site, tstamp, rank))
                self.out('Processed {0}'.format(basename))


def iter_alexa_zip_file(fname):
    """ Returns an iterator yielding a tuple `(rank, entry)` for every
    line it finds in the file in the archive `fname`.

    The standard Alexa Top1M data is a :class:`zipfile.ZipFile`. The
    archive contains one file named `top-1m.csv`. The lines in this
    file have the form `rank,site` (no spaces!).
    """
    with ZipFile(fname) as zf:
        # The archive contains one file named ``top-1m.csv``
        for line in zf.open('top-1m.csv'):
            rank, name = line.decode().strip().split(',', 1)
            yield (name, rank)
