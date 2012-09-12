# -*- coding: utf-8 -*-

import json

import hbase.compat as comp

class HBase(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _make_request(self, *path):
        head = 'http://{0}:{1}/'.format(self.host, self.port)
        tail = '/'.join(path)
        url = head + tail
        req = comp.Request(url)
        req.headers['Accept'] = 'application/json'
        return req

    def get_tables(self):
        req = self._make_request()
        resp = comp.urlopen(req)
        parsed_json = json.loads(resp.readall().decode())
        for table_struct in parsed_json['table']:
            yield table_struct['name']
