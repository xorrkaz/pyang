"""yang-data-ext plugin

Verifies YANG data usage as defined in draft-ietf-yang-data-ext.

Verifies the grammar of the yang-data-ext extension statements.
"""

import pyang
from pyang import plugin
from pyang import grammar
from pyang import statements
from pyang import error
from pyang.error import err_add

yde_module_name = 'ietf-yang-data-ext'

class YDEPlugin(plugin.PyangPlugin):
    def __init__(self):
        plugin.PyangPlugin.__init__(self, 'yang-data-ext')

def pyang_plugin_init():
    """Called by pyang plugin framework at to initialize the plugin."""

    # Register the plugin
    plugin.register_plugin(YDEPlugin())

    # Register that we handle extensions from the YANG module 'ietf-yang-data-ext'
    grammar.register_extension_module(yde_module_name)

    yd = (yde_module_name, 'yang-data')
    statements.add_data_keyword(yd)
    statements.add_keyword_with_children(yd)
    statements.add_keywords_with_no_explicit_config(yd)

    ayd = (yde_module_name, 'augment-yang-data')
    statements.add_keyword_with_children(ayd)
    statements.add_copy_augment_keyword(ayd)
    statements.add_keyword_phase_i_children('expand_2', ayd)
    statements.add_keywords_with_no_explicit_config(ayd)

    # Register the special grammar
    for (stmt, occurance, (arg, rules), add_to_stmts) in yde_stmts:
        grammar.add_stmt((yde_module_name, stmt), (arg, rules))
        grammar.add_to_stmts_rules(add_to_stmts,
                                   [((yde_module_name, stmt), occurance)])

    # Add validation functions
    statements.add_validation_fun('expand_2',
                                  [yd],
                                  v_yang_data)
    statements.add_validation_fun('type',
                                  [ayd],
                                  v_type_augment_yang_data)
    statements.add_validation_fun('expand_2',
                                  [ayd],
                                  statements.v_expand_2_augment)

    # Register special error codes
    error.add_error_code('YDE_YANG_DATA_CHILD', 1,
                         "the 'yang-data' extension must have exactly one " +
                         "child that is a container")

yde_stmts = [

    # (<keyword>, <occurance when used>,
    #  (<argument type name | None>, <substmts>),
    #  <list of keywords where <keyword> can occur>)

    ('yang-data', '*',
     ('identifier', grammar.data_def_stmts),
     ['module', 'submodule']),

   ('augment-yang-data', '*',
    ('absolute-schema-nodeid',
     [('when', '?'),
      ('if-feature', '*'),
      ('status', '?'),
      ('description', '?'),
      ('reference', '?'),
      ('$interleave',
       [('case', '*')] +
       grammar.data_def_stmts)]),
    ['module', 'submodule']),

]

def v_yang_data(ctx, stmt):
    if (len(stmt.i_children) != 1 or
        stmt.i_children[0].keyword != 'container'):
        err_add(ctx.errors, stmt.pos, 'YDE_YANG_DATA_CHILD', ())

def v_type_augment_yang_data(ctx, stmt):
    if not stmt.arg.startswith("/"):
        stmt.i_target_node = None
        err_add(ctx.errors, stmt.pos, 'BAD_VALUE',
                (stmt.arg, "absolute-node-id"))
