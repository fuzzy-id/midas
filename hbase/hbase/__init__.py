# -*- coding: utf-8 -*-

import base64
import json

import hbase.compat as comp

def _open_and_parse(req):
    resp = comp.urlopen(req)
    return json.loads(resp.readall().decode())        

class HBase(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._base_url = 'http://{0}:{1}/'.format(self.host, self.port)

    def _make_request(self, *path, data=None):
        tail = '/'.join(path)
        url = self._base_url + tail
        headers = {'Accept': 'application/json'}
        if isinstance(data, str):
            headers['Content-Type'] = 'application/octet-stream'
            data = comp.comp_bytes(data, 'utf-8')
        elif data is not None:
            headers['Content-Type'] = 'application/json'
            data = comp.comp_bytes(json.dumps(data), 'utf-8')
        return comp.Request(url, data=data, headers=headers)

    @property
    def tables(self):
        req = self._make_request()
        parsed_json = _open_and_parse(req)
        return [ table_struct['name']
                 for table_struct in parsed_json['table'] ]

    @property
    def version(self):
        req = self._make_request('version')
        return _open_and_parse(req)

    def get_scanner(self, table, batch=1):
        req = self._make_request(table, 'scanner', data={'Scanner': {'batch': batch}})
        resp = comp.urlopen(req)
        scanner_loc = resp.headers['Location']
        req = comp.Request(scanner_loc, headers={'Accept': 'application/json'})
        resp = comp.urlopen(req)
        while resp.code == 200:
            yield json.loads(resp.readall().decode(), object_hook=my_hook)
            req = comp.Request(scanner_loc, headers={'Accept': 'application/json'})
            resp = comp.urlopen(req)

    def put_cell(self, table, row, col, data):
        req = self._make_request(table, row, col, data=data)
        comp.urlopen(req)

def my_hook(d):
    if 'column' in d and '$' in d:  # should be a cell
        d['column'] = b64decode(d['column'])
        d['$'] = b64decode(d['$'])
    elif 'Cell' in d and 'key' in d:  # should be a row
        d['key'] = b64decode(d['key'])
    return d

def b64decode(s):
    b = bytes(s, 'utf-8')
    d = base64.b64decode(b)
    return d.decode('utf-8')
