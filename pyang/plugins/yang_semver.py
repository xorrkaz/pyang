"""YANG Semver plugin

Verifies the YANG Semver version extension of YANG revisions per RFCXXXX
"""

import re

from pyang import plugin
from pyang import syntax
from pyang import grammar

yang_semver_module_name = 'ietf-yang-semver'

re_version = re.compile(
    r"^(?P<major>[0-9]+)[.](?P<minor>[0-9]+)[.](?P<patch>[0-9]+)"
    r"(?P<compat>_(non_)?compatible)?"
    r"(?P<pre_release>-[A-Za-z0-9.-]+)?"
    r"(?P<build>[+][A-Za-z0-9.-]+)?$")

class YANGSemverPlugin(plugin.PyangPlugin):
    pass

def _chk_version(s):
    return re_version.search(s) is not None

def parse_version(version):
    m = re_version.search(version)
    if m is None:
        return None
    compat = m.group('compat')
    if compat is not None:
        compat = compat[1:]
    return {
        'major': int(m.group('major')),
        'minor': int(m.group('minor')),
        'patch': int(m.group('patch')),
        'compat': compat,
        'pre_release': m.group('pre_release'),
        'build': m.group('build'),
    }

def format_version(major, minor, patch, compat=None):
    version = "%d.%d.%d" % (major, minor, patch)
    if compat is not None:
        version += "_" + compat
    return version

def recommend_version(old_version, change, known_versions=None):
    parsed = parse_version(old_version)
    if parsed is None:
        return None, "invalid ysv:version"
    if parsed['major'] == 0:
        return None, "pre-release MAJOR version"
    if parsed['pre_release'] is not None or parsed['build'] is not None:
        return None, "pre-release metadata present"
    known_versions = set(known_versions or [])

    major = parsed['major']
    minor = parsed['minor']
    patch = parsed['patch']
    compat = parsed['compat']

    if change == 'nbc':
        candidate = format_version(major + 1, 0, 0)
        if candidate in known_versions:
            return format_version(major, minor, patch + 1, 'non_compatible'), None
        return candidate, None
    if change == 'bc':
        if compat is None:
            candidate = format_version(major, minor + 1, 0)
            if candidate in known_versions:
                return format_version(major, minor, patch + 1, 'compatible'), None
            return candidate, None
        return format_version(major, minor, patch + 1, compat), None
    if change == 'editorial':
        return format_version(major, minor, patch + 1, compat), None
    return None, "unknown change type"

def pyang_plugin_init():
    """Called by pyang plugin framework at to initialize the plugin."""

    # Register the plugin
    plugin.register_plugin(YANGSemverPlugin())

    # Add our special argument syntax checkers
    syntax.add_arg_type('yang-semver', _chk_version)

    # Register that we handle extensions from the YANG module 'ietf-yang-semver'
    grammar.register_extension_module(yang_semver_module_name)

    # Register the special grammar
    for stmt, occurence, (arg, rules), add_to_stmts in yang_semver_stmts:
        grammar.add_stmt((yang_semver_module_name, stmt), (arg, rules))
        grammar.add_to_stmts_rules(add_to_stmts,
                                   [((yang_semver_module_name, stmt), occurence)])

yang_semver_stmts = [

    # (<keyword>, <occurence when used>,
    #  (<argument type name | None>, <substmts>),
    #  <list of keywords where <keyword> can occur>)

    ('version', '?',
     ('yang-semver', []),
     ['revision']),
]
