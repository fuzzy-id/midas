# -*- coding: utf-8 -*-

import json
import os.path

from crawlcrunch.compat import GzipFile

class ZippedJsonFile(object):

    def __init__(self, path):
        self.path = path
        self.data = None

    def exists(self):
        return os.path.isfile(self.path)

    def load(self):
        with GzipFile(self.path, 'rb') as fp:
            self.data = json.load(fp)

    def dump(self, data=None):
        if data is not None:
            self.data = data
        with GzipFile(self.path, 'wb') as fp:
            json.dump(self.data, fp)
