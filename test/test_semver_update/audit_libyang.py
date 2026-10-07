"""Compare this checkout with an external libyang schema-comparison suite."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    modules = args.suite.parents[2] / 'modules'
    env = os.environ.copy()
    env['PYTHONPATH'] = str(root)
    total = 0
    deviations = 0
    classification_deviations = 0
    for category in ('bc', 'ed', 'nbc', 'local_full_resolved'):
        for path in sorted((args.suite / category).rglob('*_cmp.json')):
            with path.open() as stream:
                data = json.load(stream)
            comparisons = data[
                'ietf-yang-schema-comparison-output:schema-comparison'][
                    'comparison']
            for comparison in comparisons:
                old = comparison['source']
                new = comparison['target']
                oldpath = path.parent / ('%s@%s.yang' %
                                         (old['module'], old['revision']))
                newpath = path.parent / ('%s@%s.yang' %
                                         (new['module'], new['revision']))
                result = subprocess.run(
                    [sys.executable, str(root / 'bin/pyang'),
                     '-p', str(path.parent), '-p', str(modules),
                     '-P', str(path.parent), '-P', str(modules),
                     '--print-error-code', '--check-update-from', str(oldpath),
                     '--check-update-semver', str(newpath)],
                    env=env, capture_output=True, text=True, check=False)
                suggested = next((line.split(': ', 1)[1]
                                  for line in result.stdout.splitlines()
                                  if line.startswith('SUGGESTED-NEXT-')), None)
                expected = comparison['suggested-target-version']
                if 'POSSIBLE-NBC-CHANGE(S):' in result.stdout:
                    actual = 'possible-nbc'
                elif 'NBC-CHANGE(S):' in result.stdout:
                    actual = 'non-backwards-compatible'
                elif suggested == '1.1.0':
                    actual = 'backwards-compatible'
                elif suggested == '1.0.1':
                    actual = 'editorial'
                else:
                    actual = 'unavailable'
                conformance = comparison['conformance']
                total += 1
                if suggested != expected:
                    deviations += 1
                if actual != conformance:
                    classification_deviations += 1
                if suggested != expected or actual != conformance:
                    print('%s: libyang %s (%s), pyang %s (%s)' %
                          (path.relative_to(args.suite), expected, conformance,
                           suggested, actual))
                    print(result.stdout.strip())
                    print(result.stderr.strip())
                else:
                    warnings = [line for line in result.stderr.splitlines()
                                if ': warning: ' in line]
                    if warnings:
                        print('%s: additional diagnostics\n%s' %
                              (path.relative_to(args.suite),
                               '\n'.join(warnings)))
    print('%s comparisons; %s version deviations; '
          '%s classification deviations' %
          (total, deviations, classification_deviations))


if __name__ == '__main__':
    main()
