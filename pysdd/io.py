# -*- coding: UTF-8 -*-
"""
pysdd.io
~~~~~~~~

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2019 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
MYPY = False
if MYPY:
    from .sdd import SddNode, Vtree
    from typing import List, Optional, Dict, Set
    LitNameMap = Dict[int, str]


def sdd_to_dot(node, litnamemap=None, show_id=False):
    # type: (SddNode, Optional[LitNameMap], bool) -> str
    """Generate (alternative) Graphviz DOT string for SDD with given root."""
    if node is None:
        raise ValueError("No root node given")
    s = [
        "digraph sdd {"
    ]
    visited = set()
    s += _sddnode_to_dot_int(node, visited, litnamemap, show_id)
    s += [
        "}"
    ]
    return "\n".join(s)


def _format_sddnode_label(node, name=None, litnamemap=None):
    # type: (SddNode, Optional[str], Optional[LitNameMap]) -> str
    if name is not None:
        pass
    elif node.is_true():
        name = "⟙"
    elif node.is_false():
        name = "⟘"
    else:
        name = node.literal
    if litnamemap is not None:
        name = litnamemap.get(name, name)
    return f"{name}"


def _format_sddnode_xlabel(node):
    # type: (SddNode) -> str
    if node.vtree() is not None:
        vtree_pos = node.vtree().position()
    else:
        vtree_pos = "n"
    return f"Id:{node.id}\\nVp:{vtree_pos}"


def _sddnode_to_dot_int(node, visited, litnamemap=None, show_id=False):
    # type: (SddNode, Set[SddNode], Optional[LitNameMap], bool) -> List[str]
    if node in visited:
        return []
    visited.add(node)
    if node.is_false() or node.is_true() or node.is_literal():
        label = _format_sddnode_label(node, None, litnamemap)
        extra_options = ""
        if show_id:
            extra_options += (",xlabel=\"" + _format_sddnode_xlabel(node) + "\"")
        return [f"{node.id} [shape=rectangle,label=\"{label}\"{extra_options}];"]
    elif node.is_decision():
        label = _format_sddnode_label(node, '+', litnamemap)
        extra_options = ""
        if show_id:
            extra_options += (",xlabel=\"" + _format_sddnode_xlabel(node) + "\"")
        s = [f"{node.id} [shape=circle,label=\"{label}\"{extra_options}];"]
        for idx, (prime, sub) in enumerate(node.elements()):
            ps_id = "ps_{}_{}".format(node.id, idx)
            s += [
                "{} [shape=circle, label=\"×\"];".format(ps_id),
                "{} -> {} [arrowhead=none];".format(node.id, ps_id),
                "{} -> {};".format(ps_id, prime.id),
                "{} -> {};".format(ps_id, sub.id),
            ]
            s += _sddnode_to_dot_int(prime, visited, litnamemap, show_id)
            s += _sddnode_to_dot_int(sub, visited, litnamemap, show_id)
        return s


def vtree_to_dot(vtree, litnamemap=None, show_id=False):
    # type: (Vtree, Optional[LitNameMap], bool) -> str
    """Generate (alternative) Graphviz DOT string for given Vtree."""
    s = [
        "digraph vtree {"
    ]
    s += _vtree_to_dot_int(vtree, litnamemap, show_id)
    s += [
        "}"
    ]
    return "\n".join(s)


def _vtree_to_dot_int(vtree, litnamemap=None, show_id=False):
    # type: (Vtree, Optional[LitNameMap], bool) -> List[str]
    s = []
    left = vtree.left()
    right = vtree.right()
    if left is None and right is None:
        name = vtree.var()
        if litnamemap is not None:
            name = litnamemap.get(name, name)
        extra_options = ""
        if show_id:
            extra_options += f",xlabel=\"{vtree.position()}\""
        s += [f"{vtree.position()} [label=\"{name}\",shape=\"box\"{extra_options}];"]
    else:
        extra_options = ""
        if show_id:
            extra_options += f",xlabel=\"{vtree.position()}\""
        s += [f"{vtree.position()} [shape=\"point\"{extra_options}];"]
    if left is not None:
        s += [f"{vtree.position()} -> {left.position()} [arrowhead=none];"]
        s += _vtree_to_dot_int(left, litnamemap, show_id)
    if right is not None:
        s += [f"{vtree.position()} -> {right.position()} [arrowhead=none];"]
        s += _vtree_to_dot_int(right, litnamemap, show_id)
    return s


def nnf_file_wmc(nnf_filename, weights=None):
    """Perform non-smoothed Weighted Model Counting on the given NNF file.

    This is an auxiliary function to perform WMC given an NNF file with only
    Python code. This function will thus also work, even if the C SDD library
    is not available.
    """
    wmc = []  # type: List[Optional[float]]
    ln = 0
    with open(nnf_filename, 'r') as nnf_file:
        for line in nnf_file.readlines():
            cols = line.strip().split(' ')
            if cols[0] == 'c':
                continue
            if cols[0] == 'nnf':
                wmc = [None] * int(cols[1])
                continue
            if cols[0] == 'L':
                lit = int(cols[1])
                if lit in weights:
                    wmc[ln] = weights[lit]
                else:
                    wmc[ln] = 1.0
            if cols[0] == 'A':
                wmc[ln] = 1.0
                for i in range(int(cols[1])):
                    wmc[ln] *= wmc[int(cols[2 + i])]
            if cols[0] == 'O':
                wmc[ln] = 0.0
                for i in range(int(cols[2])):
                    wmc[ln] += wmc[int(cols[3 + i])]
            ln += 1
    return wmc[-1]
