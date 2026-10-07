"""Regression checks for effective nodes, metadata and dependencies."""

import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


class EffectiveUpdateTest(unittest.TestCase):

    def compare(self, old, new, version, refine=False, extra=None,
                old_version=None, new_version=None):
        with tempfile.TemporaryDirectory() as directory:
            for name, body in (extra or {}).items():
                with open(os.path.join(directory, name), 'w') as stream:
                    stream.write(body)
            paths = []
            for date, body in (('2000-01-01', old), ('2000-01-02', new)):
                if refine:
                    body = ('grouping g { %s } '
                            'container cont { uses g { %s } }' % body)
                declared = old_version if date == '2000-01-01' else new_version
                revision = 'revision %s;' % date
                if declared is not None:
                    revision = ('revision %s { ysv:version "%s"; }' %
                                (date, declared))
                if '@REV@' in body:
                    body = body.replace('@REV@', revision)
                elif body.startswith(('import ', 'include ', 'reference ')):
                    body = '%s %s' % (body, revision)
                else:
                    body = '%s %s' % (revision, body)
                if old_version is not None or new_version is not None:
                    body = 'import ietf-yang-semver { prefix ysv; } ' + body
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
            module_path = directory + os.pathsep + os.path.join(
                ROOT, 'test/test_semver_update')
            result = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'bin/pyang'),
                 '-p', module_path, '-P', module_path, '--print-error-code',
                 '--check-update-from', paths[0], '--check-update-semver',
                 '--check-update-nbc-verbose', paths[1]],
                env=env, capture_output=True, text=True, check=False)
            self.assertIn('SUGGESTED-NEXT-YANG-SEMVER: ' + version,
                          result.stdout.splitlines(),
                          result.stdout + result.stderr)
            self.assertNotIn('error: BAD', result.stderr)
            for line in result.stderr.splitlines():
                if ': error: ' in line:
                    self.assertIn(': error: CHK_', line)
            self.assertEqual(result.returncode,
                             int(': error: ' in result.stderr),
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

    def test_inherited_patterns(self):
        for keyword in ('leaf', 'leaf-list'):
            for oldpattern, newpattern, version in (
                    ('pattern "a.*";', 'pattern "b.*";', '2.0.0'),
                    ('', 'pattern "a.*";', '2.0.0'),
                    ('pattern "a.*";', '', '2.0.0'),
                    ('pattern "[a-z]+";',
                     'pattern "[a-z]+" { modifier invert-match; }', '2.0.0'),
                    ('pattern "a.*";', 'pattern "a.*";', '1.1.0')):
                with self.subTest(keyword=keyword, old=oldpattern,
                                  new=newpattern):
                    definitions = ('typedef a { type string { %s } } '
                                   'typedef b { type string { %s } } ' %
                                   (oldpattern, newpattern))
                    result = self.compare(
                        definitions + '%s x { type a; }' % keyword,
                        definitions + '%s x { type b; }' % keyword, version)
                    if version == '2.0.0':
                        self.assertIn('CHK_UNDECIDED_PATTERN', result.stderr)
                        self.assertIn('POSSIBLE-NBC-CHANGE(S):', result.stdout)
                        self.assertIn('probe:/x (pattern changed)',
                                      result.stdout)
                        self.assertIn('Consult document authors and '
                                      'YANG Doctors.',
                                      result.stdout)
                        self.assertNotIn('CHK_MISSING_NBC_EXTENSION',
                                         result.stderr)
                    else:
                        self.assertNotIn('CHK_UNDECIDED_PATTERN',
                                         result.stderr)

    def test_nested_patterns(self):
        for other, version in (('b.*', '2.0.0'), ('a.*', '1.1.0')):
            with self.subTest(other=other):
                definitions = (
                    'typedef base-a { type string { pattern "a.*"; } } '
                    'typedef base-b { type string { pattern "%s"; } } '
                    'typedef mid-a { type base-a { length "1..max"; } } '
                    'typedef mid-b { type base-b { length "1..max"; } } '
                    'typedef a { type mid-a { pattern "[a-z]+"; } } '
                    'typedef b { type mid-b { pattern "[a-z]+"; } } ' % other)
                result = self.compare(definitions + 'leaf x { type a; }',
                                      definitions + 'leaf x { type b; }',
                                      version)
                if version == '2.0.0':
                    self.assertIn('CHK_UNDECIDED_PATTERN', result.stderr)
                    self.assertIn('probe:/x (pattern changed)', result.stdout)
                else:
                    self.assertNotIn('CHK_UNDECIDED_PATTERN', result.stderr)

    def test_imported_patterns(self):
        extra = {'dep.yang':
                 'module dep { yang-version 1.1; namespace urn:dep; prefix d; '
                 'typedef a { type string { pattern "a.*"; } } '
                 'typedef b { type string { pattern "b.*"; } } }'}
        header = 'import dep { prefix d; } @REV@ '
        result = self.compare(header + 'leaf x { type d:a; }',
                              header + 'leaf x { type d:b; }',
                              '2.0.0', extra=extra)
        self.assertIn('CHK_UNDECIDED_PATTERN', result.stderr)
        self.assertIn('probe:/x (pattern changed)', result.stdout)
        old = (header + 'grouping g { leaf x { type d:a; } } '
               'container one { uses g; } container two { uses g; }')
        result = self.compare(old, old.replace('type d:a', 'type d:b'),
                              '2.0.0', extra=extra)
        self.assertIn('probe:/one/x (pattern changed)', result.stdout)
        self.assertIn('probe:/two/x (pattern changed)', result.stdout)

    def test_equivalent_patterns(self):
        self.compare('leaf x { type string { '
                     'pattern "a.*"; pattern ".*z"; } }',
                     'leaf x { type string { '
                     'pattern ".*z"; pattern "a.*"; } }',
                     '1.0.1')
        definitions = ('typedef base { type string { pattern "a.*"; } } '
                       'typedef a { type base; } '
                       'typedef b { type base { pattern "a.*"; } } ')
        result = self.compare(definitions + 'leaf x { type a; }',
                              definitions + 'leaf x { type b; }', '1.1.0')
        self.assertNotIn('CHK_UNDECIDED_PATTERN', result.stderr)

    def test_semver_version_collisions(self):
        cases = []
        for change, candidate, fallback in (
                ('nbc', '2.0.0', '1.2.4_non_compatible'),
                ('bc', '1.3.0', '1.2.4_compatible')):
            for suffix in ('', '_compatible', '_non_compatible', '+build'):
                cases.append(('1.2.3', change, [candidate + suffix], fallback))
            cases.append(('1.2.3', change, [candidate + '-alpha'], candidate))
            cases.append(('1.2.3', change,
                          [candidate, '1.2.4', '1.2.5_compatible+build'],
                          '1.2.6_' + fallback.split('_', 1)[1]))
        cases.extend([
            ('1.2.3', 'nbc',
             ['2.0.0_compatible', '1.2.4_compatible', '1.2.5_non_compatible'],
             '1.2.6_non_compatible'),
            ('1.2.3', 'bc', ['1.3.0', '1.2.4_non_compatible'],
             '1.2.5_non_compatible'),
            ('1.2.3', 'editorial', ['1.2.4'], '1.2.5'),
            ('1.2.3', 'editorial', ['1.2.4_compatible'], '1.2.5_compatible'),
            ('1.2.3', 'editorial', ['1.2.4_non_compatible'],
             '1.2.5_non_compatible'),
            ('1.2.3', 'editorial', ['1.2.4+build'], '1.2.5'),
            ('1.2.3', 'editorial', ['1.2.4-alpha'], '1.2.4'),
            ('1.2.3_compatible', 'bc', ['1.2.4_compatible'],
             '1.2.5_compatible'),
            ('1.2.3_compatible', 'editorial', ['1.2.4_non_compatible'],
             '1.2.5_non_compatible'),
            ('1.2.3_non_compatible', 'bc', ['1.2.4_non_compatible+build'],
             '1.2.5_non_compatible'),
            ('1.2.3_non_compatible', 'editorial', ['1.2.4_non_compatible'],
             '1.2.5_non_compatible')])
        for old_version, change, known_versions, suggested in cases:
            with self.subTest(old=old_version, change=change,
                              known_versions=known_versions):
                history = '@REV@ ' + ''.join(
                    'revision 1999-12-%02d { ysv:version "%s"; } ' %
                    (28 - index, version)
                    for index, version in enumerate(known_versions))
                old = history + 'leaf x { type string; }'
                new = old
                if change == 'nbc':
                    new = old.replace('type string', 'type uint32')
                elif change == 'bc':
                    new += 'leaf y { type string; }'
                self.compare(old, new, suggested, old_version=old_version)

    def test_sticky_semver_modifiers(self):
        for modifier in ('compatible', 'non_compatible'):
            old_version = '1.2.3_' + modifier
            suggested = '1.2.4_' + modifier
            for new, new_version in (
                    ('leaf x { type string; }', '1.2.5_' + modifier),
                    ('leaf x { type string; } leaf y { type string; }',
                     '1.2.5_' + modifier),
                    ('leaf x { type string; description new; }',
                     '1.2.4_' + modifier),
                    ('leaf x { type string; description new; }',
                     '1.2.5_' + modifier)):
                with self.subTest(modifier=modifier, new=new,
                                  new_version=new_version):
                    old = 'leaf x { type string; }'
                    if 'description' in new:
                        old = 'leaf x { type string; description old; }'
                    result = self.compare(old, new, suggested,
                                          old_version=old_version,
                                          new_version=new_version)
                    self.assertNotIn('CHK_BAD_SEMVER', result.stderr)
                    if 'description' in new:
                        self.assertIn('CHK_UNDECIDED_DESCRIPTION',
                                      result.stderr)

    def test_semver_nbc_modifier_bumps(self):
        for old_version, new_version, valid in (
                ('1.2.3', '1.2.4_non_compatible', True),
                ('1.2.3_compatible', '1.2.4_non_compatible', True),
                ('1.2.3_non_compatible', '1.2.4_non_compatible', True),
                ('1.2.3_non_compatible', '1.2.3_non_compatible', False),
                ('1.2.3_non_compatible', '1.2.2_non_compatible', False),
                ('1.2.3', '1.2.3_non_compatible', False),
                ('1.2.3', '1.2.2_non_compatible', False),
                ('1.2.3', '1.1.9_non_compatible', False),
                ('1.2.3', '1.3.0_non_compatible', False),
                ('1.2.3_non_compatible', '1.3.0_non_compatible', False),
                ('1.2.3_non_compatible', '2.0.0', True)):
            with self.subTest(old=old_version, new=new_version):
                result = self.compare('leaf x { type string; }',
                                      'leaf x { type uint32; }', '2.0.0',
                                      old_version=old_version,
                                      new_version=new_version)
                if valid:
                    self.assertNotIn('CHK_BAD_SEMVER_NBC_BUMP', result.stderr)
                else:
                    self.assertIn('CHK_BAD_SEMVER_NBC_BUMP', result.stderr)

    def test_semver_modifier_branch_scope(self):
        for old_version, new_version, invalid in (
                ('1.2.3_compatible', '1.2.4', True),
                ('1.2.3_non_compatible', '1.2.4', True),
                ('1.2.3_non_compatible', '1.2.4_compatible', True),
                ('1.2.3_compatible', '1.3.0', False),
                ('1.2.3_non_compatible', '1.3.0', False),
                ('1.2.3_non_compatible', '1.3.1_compatible', False),
                ('1.2.3_non_compatible', '1.3.1_non_compatible', False)):
            with self.subTest(old=old_version, new=new_version):
                modifier = old_version.split('_', 1)[1]
                result = self.compare('leaf x { type string; }',
                                      'leaf x { type string; }',
                                      '1.2.4_' + modifier,
                                      old_version=old_version,
                                      new_version=new_version)
                if invalid:
                    self.assertIn('CHK_BAD_SEMVER_COMPAT_MODIFIER',
                                  result.stderr)
                else:
                    self.assertNotIn('CHK_BAD_SEMVER', result.stderr)

    def test_semver_modifier_policy_warnings(self):
        for old_version, new_version, descriptions, diagnostic in (
                ('1.2.3', '1.2.4_non_compatible', False,
                 'CHK_BAD_SEMVER_MAJOR_WITHOUT_POSSIBLE_NBC'),
                ('1.2.3_compatible', '1.2.4_non_compatible', False,
                 'CHK_BAD_SEMVER_MAJOR_WITHOUT_POSSIBLE_NBC'),
                ('1.2.3_non_compatible', '2.0.0_non_compatible', False,
                 'CHK_BAD_SEMVER_MAJOR_WITHOUT_POSSIBLE_NBC'),
                ('1.2.3', '1.2.4_compatible', True,
                 'CHK_BAD_SEMVER_MINOR_OVERPATCH_WITH_POSSIBLE_NBC'),
                ('1.2.3_compatible', '1.3.0_compatible', True,
                 'CHK_BAD_SEMVER_MINOR_OVERPATCH_WITH_POSSIBLE_NBC'),
                ('1.2.3_non_compatible', '1.3.0_non_compatible', True,
                 'CHK_BAD_SEMVER_MINOR_OVERPATCH_WITH_POSSIBLE_NBC')):
            with self.subTest(old=old_version, new=new_version):
                old = 'leaf x { type string; }'
                new = old
                if descriptions:
                    old = 'leaf x { type string; description old; }'
                    new = 'leaf x { type string; description new; }'
                modifier = old_version[len('1.2.3'):]
                result = self.compare(old, new, '1.2.4' + modifier,
                                      old_version=old_version,
                                      new_version=new_version)
                self.assertIn(diagnostic, result.stderr)
                self.assertNotIn(': error: ', result.stderr)

    def test_action_parameters(self):
        for direction in ('input', 'output'):
            for old, new, version, diagnostic, reason in (
                    ('leaf x { type string; }', '', '2.0.0',
                     'CHK_DEF_REMOVED', 'removed'),
                    ('', 'leaf x { type string; }', '1.1.0', None, None),
                    ('', 'leaf x { type string; mandatory true; }', '2.0.0',
                     'CHK_NEW_MANDATORY', 'CHK_NEW_MANDATORY'),
                    ('leaf x { type string; }', 'leaf x { type uint32; }',
                     '2.0.0', 'CHK_BASE_TYPE_CHANGED', 'CHK_BASE_TYPE_CHANGED'),
                    ('leaf x { type uint8 { range "1..10"; } }',
                     'leaf x { type uint8 { range "5..10"; } }',
                     '2.0.0', 'CHK_RESTRICTION_CHANGED',
                     'CHK_RESTRICTION_CHANGED'),
                    ('leaf x { type string; description old; }',
                     'leaf x { type string; description new; }',
                     '1.0.1', 'CHK_UNDECIDED_DESCRIPTION', 'description'),
                    ('leaf x { type string { pattern "a.*"; } }',
                     'leaf x { type string { pattern "b.*"; } }',
                     '2.0.0', 'CHK_UNDECIDED_PATTERN', 'pattern changed'),
                    ('leaf x { type string; }', 'leaf x { type string; }',
                     '1.0.1', None, None)):
                with self.subTest(direction=direction, old=old, new=new):
                    wrapper = ('container cont { action run { %s { %%s '
                               'leaf keep { type string; } } } }' % direction)
                    result = self.compare(wrapper % old, wrapper % new,
                                          version)
                    if diagnostic is not None:
                        self.assertIn(diagnostic, result.stderr)
                        self.assertIn('probe:/cont/run/%s/x' % direction,
                                      result.stdout)
                        self.assertIn(reason, result.stdout)
                    else:
                        self.assertNotIn('CHK_', result.stderr)
                    if diagnostic in ('CHK_UNDECIDED_DESCRIPTION',
                                      'CHK_UNDECIDED_PATTERN'):
                        self.assertIn('POSSIBLE-NBC-CHANGE(S):',
                                      result.stdout)
                        self.assertNotIn('CHK_MISSING_NBC_EXTENSION',
                                         result.stderr)
                    elif version == '2.0.0':
                        self.assertIn('CHK_MISSING_NBC_EXTENSION',
                                      result.stderr)

    def test_action_parameter_instances(self):
        for direction in ('input', 'output'):
            for wrapper, paths in (
                    ('list cont { key id; leaf id { type string; } %s }',
                     ('/cont/run',)),
                    ('grouping g { %s } container one { uses g; } '
                     'container two { uses g; }',
                     ('/one/run', '/two/run')),
                    ('container cont; augment /cont { %s }',
                     ('/cont/run',))):
                with self.subTest(direction=direction, wrapper=wrapper):
                    old = wrapper % ('action run { %s { '
                                     'container params { '
                                     'leaf x { type string; } '
                                     'leaf keep { type string; } } } }' %
                                     direction)
                    result = self.compare(
                        old, old.replace('leaf x { type string; }', ''),
                        '2.0.0')
                    self.assertIn('CHK_DEF_REMOVED', result.stderr)
                    for path in paths:
                        self.assertIn('probe:%s/%s/params/x' %
                                      (path, direction), result.stdout)
                    self.assertIn('removed', result.stdout)

    def test_action_parameter_removal(self):
        for direction in ('input', 'output'):
            with self.subTest(direction=direction):
                old = ('container cont { action run { %s { '
                       'leaf x { type string; } } } }' % direction)
                result = self.compare(old, 'container cont { action run; }',
                                      '2.0.0')
                self.assertIn('CHK_DEF_REMOVED', result.stderr)
                self.assertIn('probe:/cont/run/%s/x' % direction,
                              result.stdout)

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
