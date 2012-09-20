# -*- coding: utf-8 -*-

from midas.compat import ZipFile

CUT_HASH_KEY = 2

class Entry(object):

    TS_FORMAT = '%Y-%m-%d'
    ALEXA_TS_FORMAT = 'top-1m-%Y-%m-%d.csv.zip'

    def __init__(self, name, date, rank):
        self.name = name
        self.date = date
        self.rank = rank
        self._key = None

    def format_std(self):
        " The standard format: ``NAME\tTSTAMP, RANK``. "
        date = datetime.strftime(self.date, TS_FORMAT)
        return '{e.name}\t{0}, {e.rank}'.format(date, e=self)

    def format_w_key(self):
        " ``KEY\tSTD_FORMAT`` "
        return '{0}\t{1}'.format(self.key, self.format_std())

    @property
    def key(self):
        if self._key is None:
            self._key = hashlib.sha1(self.name).hexdigest()[:CUT_HASH_KEY]
        return self._key
        

    @classmethod
    def iter_alexa_file(cls, fname):
        """ In the standard Alexa Top1M data the time-stamp is encoded
        in the filename. Hence, parsing cannot be done line-by-line
        but per file as we need the time-stamp.
        """
        fname_last = os.path.basename(fname)
        date = datetime.datetime.strptime(fname_last, cls.ALEXA_TS_FORMAT)
        with ZipFile(fname) as zf:
            # The archive contains one file named ``top-1m.csv``
            for line in zf.open('top-1m.csv'):
                rank, name = line.decode().strip().split(',', 1)
                yield cls(name, date, int(rank))
