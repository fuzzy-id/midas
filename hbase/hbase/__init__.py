# -*- coding: utf-8 -*-

import base64
import collections
import json

import hbase.compat as comp

DEFAULT_SCHEMA = comp.OrderedDict(
    [('name', 'DEFAULT'), 
     ('IS_META', False), 
     ('IS_ROOT', False), 
     ('ColumnSchema', [comp.OrderedDict([('name', 'cf'), 
                                         ('BLOCKSIZE', '65536'), 
                                         ('BLOOMFILTER', False), 
                                         ('BLOCKCACHE', True), 
                                         ('COMPRESSION', 'GZ'), 
                                         ('VERSIONS', 3), 
                                         ('TTL', -1), 
                                         ('IN_MEMORY', False)])])])

def str64decode(s):
    b = comp.comp_bytes(s, 'utf-8')
    d = base64.b64decode(b)
    return d.decode('utf-8')

def str64encode(s):
    b = comp.comp_bytes(s, 'utf-8')
    d = base64.b64encode(b)
    return d.decode('utf-8')

def open_and_parse(req):
    resp = comp.urlopen(req)
    return decode_response(resp)        

def decode_response(resp):
    s = resp.readall().decode()
    return json.loads(s, object_hook=_json_decode_hook)

def _json_decode_hook(d):
    if 'column' in d and '$' in d:  # should be a cell
        d['column'] = str64decode(d['column'])
        d['$'] = str64decode(d['$'])
    elif 'Cell' in d and 'key' in d:  # should be a row
        d['key'] = str64decode(d['key'])
    return d


class HBBase(object):

    def _make_request(self, *path, **kwargs):
        tail = '/'.join(path)
        url = self._base_url + tail
        headers = {'Accept': 'application/json'}
        data = kwargs.get('data', None)
        if isinstance(data, str):
            headers['Content-Type'] = 'application/octet-stream'
            data = comp.comp_bytes(data, 'utf-8')
        elif data is not None:
            headers['Content-Type'] = 'application/json'
            data = comp.comp_bytes(json.dumps(data), 'utf-8')
        return comp.Request(url, data=data, headers=headers)

class HBConnection(HBBase):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._base_url = 'http://{0}:{1}/'.format(self.host, self.port)

    @property
    def tables(self):
        req = self._make_request()
        parsed_json = open_and_parse(req)
        return [ table_struct['name']
                 for table_struct in parsed_json['table'] ]

    @property
    def version(self):
        req = self._make_request('version')
        return open_and_parse(req)

    @property
    def cluster_version(self):
        req = self._make_request('version', 'cluster')
        return open_and_parse(req)

    @property
    def cluster_status(self):
        req = self._make_request('status', 'cluster')
        comp.urlopen(req)

    def create_table(self, name, schema=None):
        tbl = self[name]
        if schema is None:
            schema = copy.deepcopy(DEFAULT_SCHEMA)
            schema['name'] = name
        tbl.schema = schema

    def delete_table(self, name):
        tbl = self[name]
        del tbl.schema

    def __getitem__(self, name):
        return HBTable(name, self)


class HBTable(HBBase):

    def __init__(self, name, root):
        self.name = name
        self._base_url = '{0}{1}/'.format(root._base_url, self.name)

    @property
    def schema(self):
        req = self._make_request('schema')
        return open_and_parse(req)

    @schema.setter
    def schema(self, schema):
        req = self._make_request('schema', data=schema)
        comp.urlopen(req)

    @schema.deleter
    def schema(self):
        req = self._make_request('schema')
        req.get_method = lambda : 'DELETE'
        comp.urlopen(req)

    @property
    def regions(self):
        req = self._make_request('regions')
        return open_and_parse(req)

    def scan(self, batch=1):
        req = self._make_request('scanner', 
                                 data={'Scanner': {'batch': str(batch)}})
        resp = comp.urlopen(req)
        scanner_loc = resp.headers['Location']

        def _next():
            req = comp.Request(scanner_loc, 
                               headers={'Accept': 'application/json'})
            return comp.urlopen(req)

        resp = _next()
        while resp.code == 200:
            decoded = decode_response(resp)
            for cell in decoded['Row']:
                yield Row.from_parsed_json(cell)
            resp = _next()

    def update(self, row):
        data = {'Row': [row.as_parsable_json()]}
        req = self._make_request('non-existent-row', data=data)
        comp.urlopen(req)


class Row(object):

    def __init__(self, key, cells):
        self.key = key
        self.cells = cells

    @classmethod
    def from_parsed_json(cls, js):
        cells = [ Cell.from_parsed_json(cell) 
                  for cell in js['Cell'] ]
        return cls(js['key'], cells)

    def __str__(self):
        return 'Row({0}, {1})'.format(self.key,
                                      [ str(cell) for cell in self.cells ])

    def as_parsable_json(self):
        d = comp.OrderedDict()
        d['key'] = str64encode(self.key)
        d['Cell'] = [ cell.as_parsable_json() 
                      for cell in self.cells ]
        return d


class Cell(object):

    def __init__(self, value, column, ts=None):
        self._value = value
        self.column = column
        self.ts = ts

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val):
        self.ts = None
        self._value = new_val

    def as_parsable_json(self):
        d = comp.OrderedDict()
        d['column'] = str64encode(self.column)
        d['$'] = str64encode(self.value)
        if self.ts is not None:
            d['timestamp'] = self.ts
        return d

    def __str__(self):
        return 'Cell({s.value}, {s.column}, {s.ts})'.format(s=self)

    @classmethod
    def from_parsed_json(cls, js):
        return cls(js['$'], js['column'], js['timestamp'])
