# -*- coding: utf-8 -*-

import json
import logging
import os.path
import threading

from midas.compat import GzipFile
from midas.compat import urlopen
from midas.compat import HTTPError


class LocalFilesRoot(object):
    """ This is the root object of all data traversal.
    """

    def __init__(self, path):
        self.path = path

    def get(self, name):
        if name == 'companies':
            return CompanyList(self, self.path)
        raise ValueError("No such class '{0}'".format(name))


class ZippedJsonFile(object):
    """ Implements access to local stored data, which is realized via
    compressed (gzipped) JSON files.
    """

    def __init__(self, path):
        self.path = path
        self.data = None

    def exists(self):
        return os.path.isfile(self.path)

    def load(self):
        if self.data is None:
            with GzipFile(self.path, 'rb') as fp:
                self.data = json.loads(fp.read().decode())

    def dump(self, data=None):
        if data is not None:
            self.data = data
        with GzipFile(self.path, 'wb') as fp:
            fp.write(json.dumps(self.data).encode())


class CrunchBaseFetcherMixin(object):
    """ A mixin that sums up the general way to fetch data from
    crunchbase.
    """
    to_replace = ('\x00', '\x03', '\x0b', '\x0e',
                  '\x12', '\x14', '\x1d', '\x1e', '\x1f')
    api_key = 'vqrwexbhj9s2d7fbzzj9cg57'
    companies_list_url = '?'.join(('http://api.crunchbase.com/v/1/companies.js',
                                   'api_key={0}'.format(api_key)))
    company_url_tpl = '?'.join(('http://api.crunchbase.com/v/1/company/{0}.js',
                                'api_key={0}'.format(api_key)))

    def query_url(self):  # pragma: no cover
        raise NotImplementedError()

    @classmethod
    def replace_control_chars(cls, s):
        for c in cls.to_replace:
            s = s.replace(c, '')
        return s

    def fetch(self):
        logging.info('Fetching {0}'.format(self))
        response = urlopen(self.query_url())
        content = response.read()
        s = content.decode('utf-8')
        # Some companies have control chars in theire description
        # *sigh*
        s = self.replace_control_chars(s)
        return json.loads(s)


class Company(CrunchBaseFetcherMixin):

    def __init__(self, local_data, name):
        self.local_data = local_data
        self.name = name

    def __str__(self):
        return 'Company( {0} )'.format(self.name)

    def update(self):
        self.local_data.dump(self.fetch())
        self.load()

    def is_local(self):
        return self.local_data.exists()

    def load(self):
        self.local_data.load()
        self.data = self.local_data.data

    def query_url(self):
        return self.company_url_tpl.format(self.name)


class CompanyList(CrunchBaseFetcherMixin):

    name='companies'
    suffix = '.json.gz'

    def __init__(self, root, path):
        self.root = root
        self.path = path
        self._remote_nodes = set()

    def list_not_local(self):
        for company_name in self._remote_nodes:
            company = self.get(company_name)
            if not company.is_local():
                yield company

    def list_local(self):
        for company_file in os.listdir(self.path):
            company_name = company_file.split('.')[0]
            company = self.get(company_name)
            if company.is_local():
                yield company

    def get(self, company_name):
        local_data = self.get_local_data(company_name)
        return Company(local_data, company_name)

    def expand(self, fname):
        return os.path.join(self.path,
                            '{0}{1}'.format(fname, self.suffix))

    def get_local_data(self, name):
        fname = self.expand(name)
        return ZippedJsonFile(fname)

    def query_url(self):
        return self.companies_list_url

    def update(self):
        data = self.fetch()
        for company in data:
            self._remote_nodes.add(company['permalink'])

class Updater(object):

    def __init__(self, inst_list, num_threads=1):
        self.inst_list = inst_list
        self.num_threads = num_threads
        self.semaphore = threading.Semaphore(num_threads)

    def run(self):
        self.inst_list.update()
        for inst in self.inst_list.list_not_local():
            self.semaphore.acquire()
            fetcher = Fetcher(inst, self.semaphore)
            fetcher.start()
        # Wait 'til all threads finished
        for _ in range(self.num_threads):
            self.semaphore.acquire()


class Fetcher(threading.Thread):

    def __init__(self, inst, semaphore):
        super(Fetcher, self).__init__()
        self.inst = inst
        self.semaphore = semaphore

    def run(self):
        self.make_update(0)

    def make_update(self, tries=0):
        try:
            self.inst.update()
        except HTTPError as e:
            if e.code == 404:
                logging.critical(
                    '{0}: Got 404'.format(self.inst))
            elif tries < 2 and (e.code == 503 or e.code == 504):
                logging.critical(
                    '{0}: Got 504 ({1} attempt[s])'.format(self.inst, tries + 1))
                self.make_update(tries + 1)
            else:
                logging.exception(e)
        except Exception as e:
            logging.critical(
                '{0}: An exception occured'.format(self.inst))
            logging.exception(e)
        finally:
            self.semaphore.release()
