"""Regression checks for effective nodes, metadata and dependencies."""

import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


class EffectiveUpdateTest(unittest.TestCase):

    def compare(self, old, new, version, refine=False, extra=None):
        with tempfile.TemporaryDirectory() as directory:
            for name, body in (extra or {}).items():
                with open(os.path.join(directory, name), 'w') as stream:
                    stream.write(body)
            paths = []
            for date, body in (('2000-01-01', old), ('2000-01-02', new)):
                if refine:
                    body = ('grouping g { %s } '
                            'container cont { uses g { %s } }' % body)
                if '@REV@' in body:
                    body = body.replace('@REV@', 'revision %s;' % date)
                elif body.startswith(('import ', 'include ', 'reference ')):
                    body = '%s revision %s;' % (body, date)
                else:
                    body = 'revision %s; %s' % (date, body)
                text = ('module probe { yang-version 1.1; '
                        'namespace urn:probe; '
                        'prefix p; %s }' % body)
                text = text.replace('{', '{\n').replace(';', ';\n')
                text = text.replace('}', '}\n')
                path = os.path.join(directory, 'probe@%s.yang' % date)
                with open(path, 'w') as stream:
                    stream.write(text)
                paths.append(path)
            env = os.environ.copy()
            env['PYTHONPATH'] = ROOT
            result = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'bin/pyang'),
                 '-p', directory, '-P', directory, '--print-error-code',
                 '--check-update-from', paths[0], '--check-update-semver',
                 '--check-update-nbc-verbose', paths[1]],
                env=env, capture_output=True, text=True, check=False)
            self.assertIn('SUGGESTED-NEXT-YANG-SEMVER: ' + version,
                          result.stdout, result.stdout + result.stderr)
            self.assertNotIn('error: BAD', result.stderr)
            for line in result.stderr.splitlines():
                if ': error: ' in line:
                    self.assertIn(': error: CHK_', line)
            self.assertEqual(result.returncode,
                             int('NBC: check_update' in result.stdout),
                             result.stdout + result.stderr)
            return result

    def test_interval_restrictions(self):
        for type_, keyword in (('uint8', 'range'), ('string', 'length'),
                               ('binary', 'length')):
            for old, new, version in (
                    ('min..10', '5..10', '2.0.0'),
                    ('5..10', 'min..10', '1.1.0'),
                    ('5..max', '5..10', '2.0.0'),
                    ('5..10', '5..max', '1.1.0'),
                    ('min..max', '5..10', '2.0.0'),
                    ('5..10', 'min..max', '1.1.0'),
                    ('1..10', '1..5 | 6..10', '1.0.1'),
                    ('1..5 | 6..10', '1..10', '1.0.1'),
                    ('1..10', '1..5 | 7..10', '2.0.0'),
                    ('1..5 | 7..10', '1..10', '1.1.0'),
                    ('1 | 2 | 3', '1..3', '1.0.1'),
                    ('1..10', '5', '2.0.0'),
                    ('', 'min..max', '1.0.1'),
                    ('min..max', '', '1.0.1'),
                    ('max', 'max', '1.0.1')):
                with self.subTest(type=type_, old=old, new=new):
                    oldstmt = '%s "%s";' % (keyword, old) if old else ''
                    newstmt = '%s "%s";' % (keyword, new) if new else ''
                    result = self.compare(
                        'leaf x { type %s { %s } }' % (type_, oldstmt),
                        'leaf x { type %s { %s } }' % (type_, newstmt), version)
                    if version == '2.0.0':
                        self.assertIn('CHK_RESTRICTION_CHANGED_v1.1',
                                      result.stderr)
                        self.assertIn('CHK_MISSING_NBC_EXTENSION', result.stderr)

    def test_inherited_interval_bounds(self):
        for type_, keyword in (('uint8', 'range'), ('string', 'length')):
            definition = 'typedef t { type %s { %s "5..10"; } } ' % (
                type_, keyword)
            old = definition + 'leaf x { type t { %s "min..max"; } }' % keyword
            new = definition + 'leaf x { type t { %s "6..10"; } }' % keyword
            self.compare(old, new, '2.0.0')
            self.compare(new, old, '1.1.0')
            self.compare(old, definition + 'leaf x { type t; }', '1.0.1')

    def test_decimal_interval_restrictions(self):
        for old, new, version in (
                ('min..10.00', '5.00..10.00', '2.0.0'),
                ('5.00..max', '5.00..10.00', '2.0.0'),
                ('5.00..10.00', 'min..max', '1.1.0'),
                ('1.00..1.10', '1.00..1.05 | 1.06..1.10', '1.0.1'),
                ('-1.10..-1.00', '-1.10..-1.05 | -1.04..-1.00', '1.0.1'),
                ('1.00..1.10', '1.00..1.05 | 1.07..1.10', '2.0.0')):
            with self.subTest(old=old, new=new):
                definition = 'leaf x { type decimal64 { fraction-digits 2; '
                self.compare(definition + 'range "%s"; } }' % old,
                             definition + 'range "%s"; } }' % new, version)

    def test_defaults(self):
        for keyword in ('leaf', 'leaf-list'):
            for old, new, version in (('', 'default a;', '1.1.0'),
                                      ('default a;', '', '2.0.0'),
                                      ('default a;', 'default b;', '2.0.0')):
                with self.subTest(keyword=keyword, old=old, new=new):
                    self.compare('%s x { type string; %s }' % (keyword, old),
                                 '%s x { type string; %s }' % (keyword, new),
                                 version)
        self.compare('leaf-list x { type string; default a; default b; }',
                     'leaf-list x { type string; default b; default a; }',
                     '1.0.1')
        self.compare('leaf-list x { type string; default a; default b; }',
                     'leaf-list x { type string; default a; }', '2.0.0')
        self.compare('leaf-list x { type string; default a; }',
                     'leaf-list x { type string; default a; default b; }',
                     '1.1.0')

    def test_cardinality_defaults(self):
        for old, new, version in (
                ('', 'max-elements unbounded;', '1.0.1'),
                ('max-elements unbounded;', '', '1.0.1'),
                ('max-elements 5;', 'max-elements unbounded;', '1.1.0'),
                ('max-elements 5;', '', '1.1.0'),
                ('max-elements unbounded;', 'max-elements 5;', '2.0.0'),
                ('', 'max-elements 5;', '2.0.0'),
                ('', 'min-elements 0;', '1.0.1'),
                ('min-elements 0;', '', '1.0.1'),
                ('min-elements 5;', 'min-elements 0;', '1.1.0'),
                ('min-elements 5;', '', '1.1.0')):
            with self.subTest(old=old, new=new):
                self.compare('leaf-list x { type string; %s }' % old,
                             'leaf-list x { type string; %s }' % new, version)

    def test_implicit_defaults(self):
        for keyword in ('leaf', 'leaf-list'):
            prefix = 'typedef t { type string; default a; } '
            old = prefix + '%s x { type t; }' % keyword
            self.compare(old, prefix + '%s x { type t; default a; }' % keyword,
                         '1.0.1')
            self.compare(old, prefix + '%s x { type t; default b; }' % keyword,
                         '2.0.0')
            self.compare(prefix + '%s x { type t; default b; }' % keyword,
                         old, '2.0.0')

    def test_choice_and_mandatory(self):
        choice = ('choice x { %s case a { leaf aa { type string; } } '
                  'case b { leaf bb { type string; } } }')
        self.compare(choice % '', choice % 'default a;', '1.1.0')
        self.compare(choice % 'default a;', choice % '', '2.0.0')
        self.compare(choice % 'default a;', choice % 'default b;', '2.0.0')
        for keyword in ('anyxml', 'anydata'):
            self.compare('%s x;' % keyword,
                         '%s x { mandatory true; }' % keyword, '2.0.0')

    def test_refinements(self):
        for definition, old, new, version in (
                ('leaf x { type string; }', 'default a;', 'default b;',
                 '2.0.0'),
                ('leaf-list x { type string; }', 'default a;', 'default b;',
                 '2.0.0'),
                ('anydata x;', 'mandatory false;', 'mandatory true;', '2.0.0'),
                ('leaf-list x { type string; }', 'min-elements 5;',
                 'min-elements 10;', '2.0.0'),
                ('leaf-list x { type string; }', 'min-elements 10;',
                 'min-elements 5;', '1.1.0'),
                ('leaf x { type string; }', '', 'reference added;', '1.1.0'),
                ('leaf x { type string; reference old; }', 'reference old;',
                 'reference new;', '1.1.0')):
            with self.subTest(definition=definition, old=old, new=new):
                result = self.compare((definition, 'refine x { %s }' % old),
                                      (definition, 'refine x { %s }' % new),
                                      version, refine=True)
                if version == '2.0.0':
                    self.assertIn('/cont/x', result.stdout)
        choice = ('choice x { case a { leaf aa { type string; } } '
                  'case b { leaf bb { type string; } } }')
        result = self.compare((choice, 'refine x { default a; }'),
                              (choice, 'refine x { default b; }'),
                              '2.0.0', refine=True)
        self.assertIn('/cont/x', result.stdout)

    def test_imported_refinements(self):
        extra = {'dep.yang': 'module dep { yang-version 1.1; '
                 'namespace urn:dep; '
                 'prefix d; grouping g { leaf-list fl { type string; } } }'}
        old = ('import dep { prefix d; } @REV@ '
               'container cont { uses d:g { refine fl { min-elements 5; } } }')
        # Keep imports before the revision in the generated module.
        result = self.compare(old, old.replace('min-elements 5',
                                              'min-elements 10'),
                              '2.0.0', extra=extra)
        self.assertIn('/cont/fl', result.stdout)
        self.assertIn('changed min-elements 10 (was 5)', result.stdout)

    def test_additional_refinements(self):
        leaf = 'leaf x { type string; }'
        leaf_list = 'leaf-list x { type string; }'
        for definition, old, new, version in (
                (leaf, '', 'default a;', '1.1.0'),
                (leaf, 'default a;', '', '2.0.0'),
                (leaf_list, '', 'default a; default b;', '1.1.0'),
                (leaf_list, 'default a; default b;', 'default a;', '2.0.0'),
                ('anyxml x;', '', 'mandatory true;', '2.0.0'),
                (leaf, '', 'mandatory true;', '2.0.0'),
                (leaf_list, 'max-elements 5;', 'max-elements 10;', '1.1.0'),
                (leaf_list, 'max-elements 10;', 'max-elements 5;', '2.0.0'),
                (leaf, 'reference old;', '', '2.0.0'),
                (leaf, 'description old;', '', '2.0.0'),
                (leaf, 'description old;', 'description new;', '1.0.1'),
                (leaf, '', 'must "true()";', '2.0.0'),
                (leaf, 'must "true()";', 'must "false()";', '2.0.0'),
                ('container x;', 'presence old;', 'presence new;', '1.0.1')):
            with self.subTest(definition=definition, old=old, new=new):
                result = self.compare((definition, 'refine x { %s }' % old),
                                      (definition, 'refine x { %s }' % new),
                                      version, refine=True)
                if version != '1.1.0':
                    self.assertIn('/cont/x', result.stdout)
        definition = 'leaf-list x { type string; default a; default b; }'
        self.compare((definition, 'refine x { default c; default d; }'),
                     (definition, 'refine x { default c; default e; }'),
                     '2.0.0', refine=True)
        self.compare((definition, ''),
                     (definition, 'refine x { default b; default a; }'),
                     '1.0.1', refine=True)

    def test_references(self):
        for definition in ('leaf x { type string; %s }',
                           'typedef t { type string; %s }', '%s'):
            for old, new, version in (('', 'reference added;', '1.1.0'),
                                      ('reference old;', 'reference new;',
                                       '1.1.0'),
                                      ('reference old;', '', '2.0.0')):
                self.compare(definition % old, definition % new, version)

    def test_dependencies(self):
        for keyword in ('import', 'include'):
            if keyword == 'import':
                dependency = ('module dep { yang-version 1.1; '
                              'namespace urn:dep; prefix d; revision %s; }')
                template = 'import dep { prefix d; %s }'
            else:
                dependency = ('submodule dep { yang-version 1.1; '
                              'belongs-to probe { prefix p; } revision %s; }')
                template = 'include dep { %s }'
            extra = {'dep@%s.yang' % date: dependency % date
                     for date in ('2000-01-01', '2000-01-02')}
            for old, new in (('revision-date 2000-01-01;',
                             'revision-date 2000-01-02;'),
                            ('', 'revision-date 2000-01-02;'),
                            ('revision-date 2000-01-01;', '')):
                self.compare(template % old, template % new, '2.0.0',
                             extra=extra)
            self.compare('', template % '', '1.1.0', extra=extra)
            self.compare(template % '', '', '2.0.0', extra=extra)

    def test_multiple_instances(self):
        old = ('grouping g { leaf x { type string; default a; } } '
               'container one { uses g; } container two { uses g; }')
        result = self.compare(old, old.replace('default a', 'default b'),
                              '2.0.0')
        self.assertIn('/one/x', result.stdout)
        self.assertIn('/two/x', result.stdout)
        self.assertIn('changed default b (was a)', result.stdout)
        old = ('grouping g { leaf x { type string { pattern a; } } } '
               'container one { uses g; } container two { uses g; }')
        result = self.compare(old, old.replace('pattern a', 'pattern b'),
                              '2.0.0')
        self.assertIn('/one/x', result.stdout)
        self.assertIn('/two/x', result.stdout)
        self.assertIn('pattern changed', result.stdout)


if __name__ == '__main__':
    unittest.main()
