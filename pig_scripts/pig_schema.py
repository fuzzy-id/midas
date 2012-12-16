#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
import functools
import unittest

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
        if typ not in ('chararray', 'int'):
            raise TypeError("Unknown schema '{}'".format(schema))
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

def get_field_name(schema):
    name, _, tail = schema.partition(':')
    return name.strip(), tail.lstrip()

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

def make_serializer(schema):
    if isinstance(schema, str):
        serializer = SIMPLE_SERIALIZER[schema]
        def root_serializer(s):
            return serializer(s)
    return root_serializer

def pig_input(schema):
    as_struct = pig_schema_to_py_struct(schema)
    parser = make_parser(as_struct)
    def decorator(fn):
        def iter_input(iterator):
            for i in iterator:
                yield fn(parser(i))
        return iter_input
    return decorator

def pig_output(schema):
    as_struct = pig_schema_to_py_struct(schema)
    serializer = make_serializer(as_struct)
    def decorator(fn):
        def func(*args, **kwargs):
            for i in fn(*args, **kwargs):
                print(serializer(i))
        return func
    return decorator

class InputDecoratorTests(unittest.TestCase):

    def test_on_a_single_string(self):

        @pig_input('a: chararray')
        def a_func(s):
            return s

        result = list(a_func(['foo\n', 'bar\n']))
        self.assertEqual(result, ['foo', 'bar'])


class OutputDecoratorTests(unittest.TestCase):

    def setUp(self):
        self.out = []

        def print_mock(s):
            self.out.append(s)

        global print
        self.old_print = print
        print = print_mock

    def tearDown(self):
        global print
        print = self.old_print

    def test_print_mock(self):
        print('foo')
        self.assertEqual(self.out, ['foo'])
        
    @unittest.skip('later')
    def test_on_single_str(self):
        
        @pig_output('a: chararray')
        def a_func():
            yield 'foo'
            yield 'bar'

        result = a_func()
        self.assertEqual(result, ['foo', 'bar'])
        

class PigSchemaToPyStructTests(unittest.TestCase):
    
    def test_one_simple_type(self):
        self.assertEqual(pig_schema_to_py_struct('a: chararray'), 'chararray')
        self.assertEqual(pig_schema_to_py_struct('i: int'), 'int')

    def test_simple_outer_tuple(self):
        self.assertEqual(pig_schema_to_py_struct('()'), ())

    def test_tuple_with_fields(self):
        self.assertEqual(pig_schema_to_py_struct('(a: chararray, i: int)'),
                         (('a', 'chararray'), ('i', 'int')))
    
    def test_tuple_with_tuples(self):
        s = '(t1: tuple(a: chararray, b: int), t2: tuple(b: chararray, c: int))'
        self.assertEqual(pig_schema_to_py_struct(s), 
                         (('t1', (('a', 'chararray'), ('b', 'int'))),
                          ('t2', (('b', 'chararray'), ('c', 'int')))))

    def test_tuple_with_bag(self):
        s = '(b: bag{(a: chararray, b: int)})'
        expected = (('b', [(('a', 'chararray'), ('b', 'int'))]), )
        self.assertEqual(pig_schema_to_py_struct(s), expected)
        s = '(b: bag{tuple(a: chararray, b: int)})'
        self.assertEqual(pig_schema_to_py_struct(s), expected)

    def test_mixed_complex(self):
        s = ','.join(['(s: chararray, t: tuple(i: int, s: chararray)',
                      'b: bag{(s: chararray, i: int)})'])
        expected = (('s', 'chararray'), 
                    ('t', (('i', 'int'), ('s', 'chararray'))),
                    ('b', [(('s', 'chararray'), ('i', 'int'))]))
        self.assertEqual(pig_schema_to_py_struct(s), expected)


class MakeParserTests(unittest.TestCase):

    def test_just_a_str(self):
        parser = make_parser('chararray')
        self.assertEqual(parser('\n'), None)
        self.assertEqual(parser('\t\n'), '\t')
        self.assertEqual(parser('foo\n'), 'foo')
        self.assertEqual(parser('\tfoo\n'), '\tfoo')
        self.assertEqual(parser('foo\t\n'), 'foo\t')
        self.assertEqual(parser('\tfoo\t\n'), '\tfoo\t')

    def test_just_a_int(self):
        parser = make_parser('int')
        self.assertEqual(parser('8\n'), 8)
        self.assertEqual(parser('\n'), None)

    def test_a_tuple_with_str(self):
        parser = make_parser((('s', 'chararray'), ))
        self.assertEqual(parser('foo\n'), ('foo', ))
        self.assertEqual(parser('foo\n'), ('foo', ))
        self.assertEqual(parser('foo\t\n'), ('foo\t', ))

    def test_a_tuple_with_str_and_int(self):
        parser = make_parser((('s', 'chararray'), ('i', 'int')))
        self.assertEqual(parser('foo\t8\n'), ('foo', 8))
        self.assertEqual(parser('foo\t\n'), ('foo', None))

    def test_tuple_with_tuples(self):
        schema = (('t1', (('s', 'chararray'), ('i', 'int'))), 
                  ('t2', (('s', 'chararray'), ('i', 'int'))))
        parser = make_parser(schema)
        self.assertEqual(parser('(foo,8)\t(braz,9)\n'), 
                         (('foo', 8), ('braz', 9)))

    def test_tuple_with_bag_with_tuple(self):
        schema = (('b', [(('s', 'chararray'), ('i', 'int'))]), )
        parser = make_parser(schema)
        self.assertEqual(parser('\n'), ([], ))
        self.assertEqual(parser('{(foo,8)}\n'), ([('foo', 8)], ))
        self.assertEqual(parser('{(foo,8),(bar,10)}\n'), 
                         ([('foo', 8), ('bar', 10)], ))


class SerializerTests(unittest.TestCase):

    def test_on_simple_str(self):
        serializer = make_serializer('chararray')
        self.assertEqual(serializer('foo'), 'foo')


class FunctionalTests(unittest.TestCase):

    def test_do_not_know_why_this_should_fail(self):
        s = '(b: bag{tuple(i: int, s: chararray)}, s: chararray)'
        expected = (('b', [(('i', 'int'), ('s', 'chararray'))]), 
                    ('s', 'chararray'))
        self.assertEqual(pig_schema_to_py_struct(s), expected)
        parser = make_parser(expected)
        self.assertEqual(parser('{(1,braz),(2,iale)}\tfoo\n'),
                         ([(1, 'braz'), (2, 'iale')], 'foo'))
        self.assertEqual(parser('{(3,froz),(4,ae)}\tbar\n'),
                         ([(3, 'froz'), (4, 'ae')], 'bar'))
        self.assertEqual(parser('{(8,boz)}\t\n'),
                         ([(8, 'boz')], None))
        self.assertEqual(parser('\t\n'), ([], None))


if __name__ == '__main__':
    unittest.main()
