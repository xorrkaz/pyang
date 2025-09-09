"""YANG Semver plugin

Verifies the YANG Semver version extension of YANG revisions per RFCXXXX
"""

import re

from pyang import plugin
from pyang import syntax
from pyang import grammar

yang_semver_module_name = 'ietf-yang-semver'

re_version = re.compile(r"^[0-9]+[.][0-9]+[.][0-9]+(_(non_)?compatible)?" \
                        r"(-[A-Za-z0-9.-]+[.-][0-9]+)?([+][A-Za-z0-9.-]+)?$")

class YANGSemverPlugin(plugin.PyangPlugin):
    pass

def _chk_version(s):
    return re_version.search(s) is not None

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
