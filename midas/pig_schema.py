#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
import functools

def pig_input(schema):
    as_struct = pig_schema_to_py_struct(schema)
    parser = make_parser(as_struct)
    def decorator(fn):
        @functools.wraps(fn)
        def iter_input(iterator, *args, **kwargs):
            for i in iterator:
                for result in fn(parser(i), *args, **kwargs):
                    yield result
        return iter_input
    return decorator

def pig_output(schema):
    as_struct = pig_schema_to_py_struct(schema)
    serializer = make_serializer(as_struct)
    def decorator(fn):
        @functools.wraps(fn)
        def func(*args, **kwargs):
            for i in fn(*args, **kwargs):
                yield serializer(i)
        return func
    return decorator

def pig_schema_to_py_struct(schema):
    if schema.startswith('('):
        # We interpret this as a Tuple
        assert schema.endswith(')')
        typ, tail = pig_schema_to_py_struct_tuple(schema)
        assert tail == ''
    else:
        # The name actually doesn't matter in this case
        name, typ = get_field_name(schema)
        typ = typ.strip()
        if typ not in SIMPLE_PARSER:
            raise TypeError("Unknown schema '{0}'".format(schema))
    return typ

def pig_schema_to_py_struct_tuple(schema):
    tail = schema[1:]  # cut off the first parenthesis
    fields = []
    while True:
        if tail.startswith(')'):
            tail = tail[1:]
            break
        name, tail = get_field_name(tail)
        typ, tail = get_field_type(tail)
        if typ == 'tuple':
            typ, tail = pig_schema_to_py_struct_tuple(tail)
        if typ == 'bag':
            typ, tail = pig_schema_to_py_struct_bag(tail)
        fields.append((name, typ))
    return tuple(fields), tail
    
def pig_schema_to_py_struct_bag(schema):
    tail = schema[1:]  # cut off opening curly bracket
    tail.lstrip()
    if tail.startswith('tuple'):
        tail = tail[5:]
    typ, tail = pig_schema_to_py_struct_tuple(tail)
    assert tail.startswith('}')
    tail = tail[1:]
    return [typ, ], tail
    
def get_field_name(schema):
    name, _, tail = schema.partition(':')
    return name.strip(), tail.lstrip()

def get_field_type(schema):
    typ, _, tail = schema.partition(',')
    typ = typ.strip()
    if typ.endswith(')'):
        first_par = typ.find(')')
        tail = typ[first_par:] + tail
        typ = typ[:first_par]
    elif typ.endswith('}'):
        first_par = typ.find(')')
        tail = typ[first_par:] + tail
        typ = typ[:first_par]
    elif typ.startswith('tuple'):
        tail = ','.join([typ[5:], tail])
        typ = 'tuple'
    elif typ.startswith('bag'):
        tail = ','.join([typ[3:], tail])
        typ = 'bag'
    return typ, tail

def make_parser(schema):
    if isinstance(schema, str):
        # Just a Atom
        parser = SIMPLE_PARSER[schema]
        def root_parser(s):
            return parser(s, '\n')[0]
    else:
        # Everything else is wrapped in a tuple
        parser = make_tuple_parser(schema, '', '\t', '\n')
        def root_parser(s):
            return parser(s, '')[0]
    return root_parser

def make_tuple_parser(schema, tuple_start, delimiter, tuple_end):
    parser = []
    names = []
    for name, typ in schema:
        names.append(name)
        if isinstance(typ, tuple):
            parser.append(make_tuple_parser(typ, '(', ',', ')'))
        elif isinstance(typ, list):
            parser.append(make_bag_parser(typ))
        elif typ in SIMPLE_PARSER:
            parser.append(SIMPLE_PARSER[typ])
        else:
            raise TypeError("Cannot make parser for '{}'".format(typ))
    cls = collections.namedtuple('Tuple', ' '.join(names))
    def tuple_parser(s, end):
        assert s.startswith(tuple_start)
        tail = s[len(tuple_start):]
        fields = []
        for i, p in enumerate(parser):
            if i == len(parser) - 1:
                field, tail = p(tail, tuple_end)
                assert tail.startswith(end)
                tail = tail[len(end):]
            else:
                field, tail = p(tail, delimiter)
            fields.append(field)
        return cls(*fields), tail
    return tuple_parser

def make_bag_parser(schema):
    """ A Bag i a collection of tuples. `schema` is a list with one
    entry which defines the tuples in the bag.
    """
    assert len(schema) == 1
    sub_parser = make_tuple_parser(schema[0], '(', ',', ')')
    def bag_parser(tail, end):
        fields = []
        if tail.startswith(end):
            return fields, tail[len(end):]
        while not tail.startswith('}'):
            assert tail.startswith(',') or tail.startswith('{')
            tail = tail[1:]
            field, tail = sub_parser(tail, '')
            fields.append(field)
        tail = tail[1:]
        assert tail.startswith(end)
        tail = tail[len(end):]
        return fields, tail
    return bag_parser

def chararray_parser(s, end):
    head, _, tail = s.partition(end)
    if head == '':
        return None, tail
    return head, tail

def int_parser(s, end):
    head, _, tail = s.partition(end)
    if head == '':
        return None, tail
    return int(head), tail

SIMPLE_PARSER = {
    'chararray': chararray_parser,
    'int': int_parser,
    }

def make_serializer(schema):
    if isinstance(schema, str):
        root_serializer = SIMPLE_SERIALIZER[schema]
    else:
        root_serializer = make_tuple_serializer(schema, '', '\t', '')
    return root_serializer

def make_tuple_serializer(schema, start, delimiter, end):
    serializer = []
    attrs = []
    for name, typ in schema:
        attrs.append(name)
        if isinstance(typ, str):
            serializer.append(SIMPLE_SERIALIZER[typ])
        elif isinstance(typ, tuple):
            serializer.append(make_tuple_serializer(typ, '(', ',', ')'))
        else:
            raise TypeError("Cannot serialize '{}'".format(typ))
    def tuple_serializer(t):
        fields = ( s(getattr(t, n))
                   for s, n in zip(serializer, attrs) )
        return '{0}{1}{2}'.format(start, delimiter.join(fields), end)
    return tuple_serializer

def chararray_serializer(s):
    if s is None:
        return ''
    return s

def int_serializer(s):
    if s is None:
        return ''
    return str(s)

SIMPLE_SERIALIZER = {
    'chararray': chararray_serializer,
    'int': int_serializer,
    }
