# -*- coding: utf-8 -*-

import mock

from midas.tests.test_scripts import MDCommandTestCase


class MDCommandArgumentsTests(MDCommandTestCase):

    def _get_target_cls(self):
        from midas.scripts import MDCommand
        return MDCommand

    def test_quiet_and_always_yes_are_exclusive(self):
        obj = self.make_object()
        self.assertFalse(obj.args.always_yes)
        self.assertFalse(obj.args.quiet)
        obj = self.make_object('--quiet')
        self.assertFalse(obj.args.always_yes)
        self.assertTrue(obj.args.quiet)
        obj = self.make_object('--always_yes')
        self.assertTrue(obj.args.always_yes)
        self.assertFalse(obj.args.quiet)
        obj = self.make_object('--always_yes')
        self.assertTrue(obj.args.always_yes)
        self.assertFalse(obj.args.quiet)
        obj = self.make_object()
        with mock.patch.object(obj.parser, 'error') as error:
            error.side_effect = SystemExit
            with self.assertRaises(SystemExit):
                obj.parser.parse_args(['--quiet', '--always_yes'])
            error.assert_called_once_with(
                'argument -y/--always_yes: not allowed with argument -q/--quiet'
            )

    def test_query_user_permission(self):
        obj = self.make_object()
        with mock.patch('midas.scripts.comp_input') as comp_input:
            comp_input.return_value = 'Y'
            self.assertTrue(obj.query_user_permission('dummy query'))
            self.assert_in_cls_out('dummy query')
            comp_input.return_value = 'n'
            self.assertFalse(obj.query_user_permission('dummy query'))
            self.assert_in_cls_out('dummy query')
