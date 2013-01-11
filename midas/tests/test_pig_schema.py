# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
import collections

import mock

from midas.compat import unittest


class InputDecoratorTests(unittest.TestCase):

    def test_on_a_single_string(self):
        from midas.pig_schema import pig_input
        @pig_input('a: chararray')
        def a_func(d):
            yield d

        result = list(a_func(['foo\n', 'bar\n']))
        self.assertEqual(result, ['foo', 'bar'])


class OutputDecoratorTests(unittest.TestCase):

    def test_on_single_str(self):
        from midas.pig_schema import pig_output
        
        @pig_output('a: chararray')
        def a_func():
            yield 'foo'
            yield 'bar'

        result = list(a_func())
        self.assertEqual(result, ['foo', 'bar'])

    def test_input_and_output_decorator(self):
        from midas.pig_schema import pig_input
        from midas.pig_schema import pig_output

        @pig_output('(s: chararray, i: int)')
        @pig_input('(b: bag{(s: chararray, i: int)})')
        def a_func(row):
            for entry in row.b:
                yield entry
        
        result = list(a_func(['{(foo,8),(bar,9)}\n', '{(baz,7),(froz,6)}\n']))
        self.assertEqual(result, ['foo\t8', 'bar\t9', 'baz\t7', 'froz\t6'])


class PigSchemaToPyStructTests(unittest.TestCase):

    def _get_target(self):
        from midas.pig_schema import pig_schema_to_py_struct
        return pig_schema_to_py_struct
    
    def test_one_simple_type(self):
        pig_schema_to_py_struct = self._get_target()
        self.assertEqual(pig_schema_to_py_struct('a: chararray'), 'chararray')
        self.assertEqual(pig_schema_to_py_struct('i: int'), 'int')

    def test_simple_outer_tuple(self):
        pig_schema_to_py_struct = self._get_target()
        self.assertEqual(pig_schema_to_py_struct('()'), ())

    def test_tuple_with_fields(self):
        pig_schema_to_py_struct = self._get_target()
        self.assertEqual(pig_schema_to_py_struct('(a: chararray, i: int)'),
                         (('a', 'chararray'), ('i', 'int')))
    
    def test_tuple_with_tuples(self):
        pig_schema_to_py_struct = self._get_target()
        s = '(t1: tuple(a: chararray, b: int), t2: tuple(b: chararray, c: int))'
        self.assertEqual(pig_schema_to_py_struct(s), 
                         (('t1', (('a', 'chararray'), ('b', 'int'))),
                          ('t2', (('b', 'chararray'), ('c', 'int')))))

    def test_tuple_with_bag(self):
        pig_schema_to_py_struct = self._get_target()
        s = '(b: bag{(a: chararray, b: int)})'
        expected = (('b', [(('a', 'chararray'), ('b', 'int'))]), )
        self.assertEqual(pig_schema_to_py_struct(s), expected)
        s = '(b: bag{tuple(a: chararray, b: int)})'
        self.assertEqual(pig_schema_to_py_struct(s), expected)

    def test_mixed_complex(self):
        pig_schema_to_py_struct = self._get_target()
        s = ','.join(['(s: chararray, t: tuple(i: int, s: chararray)',
                      'b: bag{(s: chararray, i: int)})'])
        expected = (('s', 'chararray'), 
                    ('t', (('i', 'int'), ('s', 'chararray'))),
                    ('b', [(('s', 'chararray'), ('i', 'int'))]))
        self.assertEqual(pig_schema_to_py_struct(s), expected)

    def test_invalid_schema(self):
        pig_schema_to_py_struct = self._get_target()
        s = 'foo: bar'
        with self.assertRaisesRegex(TypeError, 'Unknown schema'): 
            pig_schema_to_py_struct(s)


class MakeParserTests(unittest.TestCase):

    def _get_target(self):
        from midas.pig_schema import make_parser
        return make_parser

    def test_just_a_str(self):
        make_parser = self._get_target()
        parser = make_parser('chararray')
        self.assertEqual(parser('\n'), None)
        self.assertEqual(parser('\t\n'), '\t')
        self.assertEqual(parser('foo\n'), 'foo')
        self.assertEqual(parser('\tfoo\n'), '\tfoo')
        self.assertEqual(parser('foo\t\n'), 'foo\t')
        self.assertEqual(parser('\tfoo\t\n'), '\tfoo\t')

    def test_just_a_int(self):
        make_parser = self._get_target()
        parser = make_parser('int')
        self.assertEqual(parser('8\n'), 8)
        self.assertEqual(parser('\n'), None)

    def test_just_a_date(self):
        make_parser = self._get_target()
        parser = make_parser('date')
        self.assertEqual(parser('2013-01-07\n'), datetime.date(2013, 1, 7))
        self.assertEqual(parser('\n'), None)

    def test_a_tuple_with_str(self):
        make_parser = self._get_target()
        parser = make_parser((('s', 'chararray'), ))
        self.assertEqual(parser('foo\n'), ('foo', ))
        self.assertEqual(parser('foo\n'), ('foo', ))
        self.assertEqual(parser('foo\t\n'), ('foo\t', ))

    def test_a_tuple_with_str_and_int(self):
        make_parser = self._get_target()
        parser = make_parser((('s', 'chararray'), ('i', 'int')))
        self.assertEqual(parser('foo\t8\n'), ('foo', 8))
        self.assertEqual(parser('foo\t\n'), ('foo', None))

    def test_tuple_with_tuples(self):
        make_parser = self._get_target()
        schema = (('t1', (('s', 'chararray'), ('i', 'int'))), 
                  ('t2', (('s', 'chararray'), ('i', 'int'))))
        parser = make_parser(schema)
        self.assertEqual(parser('(foo,8)\t(braz,9)\n'), 
                         (('foo', 8), ('braz', 9)))

    def test_tuple_with_bag_with_tuple(self):
        make_parser = self._get_target()
        schema = (('b', [(('s', 'chararray'), ('i', 'int'))]), )
        parser = make_parser(schema)
        self.assertEqual(parser('\n'), ([], ))
        self.assertEqual(parser('{}\n'), ([], ))
        self.assertEqual(parser('{(foo,8)}\n'), ([('foo', 8)], ))
        self.assertEqual(parser('{(foo,8),(bar,10)}\n'), 
                         ([('foo', 8), ('bar', 10)], ))

    def test_values_after_bag(self):
        make_parser = self._get_target()
        schema = (('b', [(('s', 'chararray'), ('i', 'int'))]), 
                  ('s', 'chararray'))
        parser = make_parser(schema)
        self.assertEqual(parser('{}\tfoo\n'), ([], 'foo'))


class SerializerTests(unittest.TestCase):

    def _get_target(self):
        from midas.pig_schema import make_serializer
        return make_serializer

    def test_on_simple_str(self):
        make_serializer = self._get_target()
        serializer = make_serializer('chararray')
        self.assertEqual(serializer('foo'), 'foo')
        self.assertEqual(serializer(None), '')

    def test_on_simple_int(self):
        make_serializer = self._get_target()
        serializer = make_serializer('int')
        self.assertEqual(serializer(8), '8')
        self.assertEqual(serializer(None), '')

    def test_on_tuple_with_str(self):
        make_serializer = self._get_target()
        nt = collections.namedtuple('Tuple', 's i')
        serializer = make_serializer((('s', 'chararray'), ('i', 'int')))
        self.assertEqual(serializer(nt('foo', 8)), 'foo\t8')
        self.assertEqual(serializer(nt(None, 8)), '\t8')
        self.assertEqual(serializer(nt('foo', None)), 'foo\t')

    def test_on_tuple_with_tuples(self):
        make_serializer = self._get_target()
        outer = collections.namedtuple('Tuple', 't1 t2')
        inner = collections.namedtuple('Tuple', 's i')
        serializer = make_serializer((('t1', (('s', 'chararray'), 
                                              ('i', 'int'))),
                                      ('t2', (('s', 'chararray'), 
                                              ('i', 'int')))))
        self.assertEqual(serializer(outer(inner('foo', 8), 
                                          inner('bar', 9))), 
                                    '(foo,8)\t(bar,9)')
        self.assertEqual(serializer(outer(inner(None, 8),
                                          inner('foo', None))), 
                                    '(,8)\t(foo,)')


class FunctionalTests(unittest.TestCase):

    def test_do_not_know_why_this_should_fail(self):
        from midas.pig_schema import pig_schema_to_py_struct
        from midas.pig_schema import make_parser
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


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
