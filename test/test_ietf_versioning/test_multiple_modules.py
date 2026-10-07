"""Regression checks for per-module IETF revision validation."""

import itertools
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
FIXTURES = os.path.join(ROOT, 'test/test_ietf_versioning')


class MultipleModuleTest(unittest.TestCase):

    def setUp(self):
        path = os.path.join(FIXTURES, 'ietf-missing-semver.yang')
        with open(path) as stream:
            self.header = stream.read().split('  revision ', 1)[0]

    def write_module(self, directory, name, versions, imports='',
                     belongs_to=None):
        header = self.header.replace('ietf-missing-semver', name)
        if belongs_to is not None:
            header = header.replace('module %s {' % name,
                                    'submodule %s {' % name)
            header = '\n'.join(line for line in header.split('\n')
                               if not line.startswith(('  namespace ',
                                                       '  prefix ')))
            header = header.replace(
                '  yang-version 1.1;',
                '  yang-version 1.1;\n  belongs-to %s { prefix ims; }' %
                belongs_to)
        if any(version is not None for date, version in versions):
            imports = '  import ietf-yang-semver { prefix ysv; }\n' + imports
        header = header.replace('  organization', imports + '\n  organization')
        revisions = []
        for date, version in versions:
            semver = '' if version is None else 'ysv:version "%s";' % version
            revisions.append('  revision %s {\n'
                             '    description "Test revision.";\n'
                             '    reference "RFC XXXX: Example.";\n'
                             '    %s\n  }\n' % (date, semver))
        path = os.path.join(directory, name + '.yang')
        with open(path, 'w') as stream:
            stream.write(header + ''.join(revisions) + '}\n')
        return path

    def check_modules(self, directory, modules, missing):
        env = os.environ.copy()
        env['PYTHONPATH'] = ROOT
        env['YANG_INSTALL'] = directory
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, 'bin/pyang'),
             '--ietf', '--print-error-code', '-p',
             directory + os.pathsep + FIXTURES] + modules,
            env=env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        warnings = [line for line in result.stderr.splitlines()
                    if 'IETF_MISSING_YANG_SEMVER' in line]
        self.assertCountEqual(
            [os.path.basename(line.split(':', 1)[0]) for line in warnings],
            [name + '.yang' for name in missing], result.stderr)
        return result

    def test_existing_modules_both_orders(self):
        modules = [os.path.join(FIXTURES, name + '.yang') for name in
                   ('ietf-missing-semver', 'ietf-missing-nbc')]
        for order in (modules, list(reversed(modules))):
            with self.subTest(order=order):
                result = self.check_modules(FIXTURES, order,
                                            ['ietf-missing-semver'])
                self.assertIn('IETF_MISSING_NBC_EXTENSION', result.stderr)

    def test_missing_in_each_module(self):
        with tempfile.TemporaryDirectory() as directory:
            modules = [self.write_module(directory, name,
                       [('2025-01-01', version)]) for name, version in
                       (('ietf-a', None), ('ietf-b', None),
                        ('ietf-c', '1.0.0'))]
            for order in itertools.permutations(modules):
                with self.subTest(order=order):
                    self.check_modules(directory, list(order),
                                       ['ietf-a', 'ietf-b'])

    def test_latest_revision_only(self):
        for latest, previous in ((None, '1.0.0'), ('1.0.1', None)):
            versions = [('2025-01-01', latest), ('2024-01-01', previous)]
            for order in (versions, list(reversed(versions))):
                with self.subTest(order=order):
                    with tempfile.TemporaryDirectory() as directory:
                        path = self.write_module(directory, 'ietf-a', order)
                        missing = ['ietf-a'] if latest is None else []
                        result = self.check_modules(directory, [path], missing)
                        if latest is None:
                            with open(path) as stream:
                                lines = stream.readlines()
                            line = next(index + 1 for index, text in
                                        enumerate(lines) if
                                        'revision 2025-01-01' in text)
                            self.assertIn('%s:%d: warning: '
                                          'IETF_MISSING_YANG_SEMVER' %
                                          (path, line), result.stderr)

    def test_imported_module_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            dep = self.write_module(directory, 'ietf-dep',
                                    [('2025-01-01', None)])
            main = self.write_module(
                directory, 'ietf-main', [('2025-01-01', None)],
                '  import ietf-dep { prefix dep; }\n')
            self.check_modules(directory, [main], ['ietf-main'])
            for order in ([dep, main], [main, dep]):
                with self.subTest(order=order):
                    self.check_modules(directory, order,
                                       ['ietf-main', 'ietf-dep'])

    def test_submodule_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = self.write_module(
                directory, 'ietf-parent', [('2025-01-01', '1.0.0')],
                '  include ietf-sub;\n')
            sub = self.write_module(directory, 'ietf-sub',
                                    [('2025-01-01', None)],
                                    belongs_to='ietf-parent')
            self.check_modules(directory, [parent], [])
            for order in ([parent, sub], [sub, parent]):
                with self.subTest(order=order):
                    self.check_modules(directory, order, ['ietf-sub'])


if __name__ == '__main__':
    unittest.main()
