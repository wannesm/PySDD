# -*- coding: UTF-8 -*-
"""
pysdd.util
~~~~~~~~~~

Utility functions on top of the ``sdd`` package.

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2019 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import math
import array
from .sdd import SddNode, SddManager, Vtree


MYPY = False
if MYPY:
    # from .sdd import Vtree
    from typing import List, Optional, Dict, Set, Union, Tuple
    LitNameMap = Dict[Union[int, str], str]


node_count = 0


def sdd_to_dot(node, litnamemap=None, show_id=False, merge_leafs=False):
    # type: (Union[SddNode, SddManager], Optional[LitNameMap], bool, bool) -> str
    """Generate (alternative) Graphviz DOT string for SDD with given root.

    This method is an alternative to SddManager.dot() and SddNode.dot().

    :param node: Root node for graph or SddManager
    :param litnamemap: Dictionary for node labels. For variable 1 the keys are 1 and -1 for positive and negative.
        For multiplication and addition the keys are 'mult' and 'add'. And for true and false, the keys are 'true'
        and 'false'.
    :param show_id: Show internal node ids, useful for debugging
    :param merge_leafs: Variable nodes are shown multiple times to improve the visualisation. Set this argument
        to True to disable this.
    :return: String in the Graphviz DOT format
    """
    if isinstance(node, SddNode):
        nodes = [node]
    elif isinstance(node, SddManager):
        mgr = node
        vtree = mgr.vtree()
        nodes = vtree.get_sdd_rootnodes(mgr)
    else:
        raise AttributeError(f"Unknown type {type(node)}")
    global node_count
    node_count = 0
    if litnamemap is None:
        litnamemap = {}
    if node is None:
        raise ValueError("No root node given")
    s = [
        "digraph sdd {",
        "overlap=false;"
    ]
    visited = set()
    for node in nodes:
        nodeid, root_s = _sddnode_to_dot_int(node, visited, litnamemap, show_id, merge_leafs)
        s += root_s
    s += [
        "}"
    ]
    return "\n".join(s)


def _format_sddnode_label(node, name=None, litnamemap=None):
    # type: (SddNode, Optional[str], Optional[LitNameMap]) -> str
    if name is not None:
        pass
    elif node.is_true():
        name = litnamemap.get("true", "⟙")
    elif node.is_false():
        name = litnamemap.get("false", "⟘")
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


def _sddnode_to_dot_int(node, visited, litnamemap=None, show_id=False, merge_leafs=False):
    # type: (SddNode, Set[SddNode], Optional[LitNameMap], bool, bool) -> Tuple[str, List[str]]
    if node in visited:
        return str(node.id), []
    if node.is_false() or node.is_true() or node.is_literal():
        # Leaf node
        if merge_leafs:
            visited.add(node)
        label = _format_sddnode_label(node, None, litnamemap)
        extra_options = ""
        if show_id:
            extra_options += (",xlabel=\"" + _format_sddnode_xlabel(node) + "\"")
        if merge_leafs:
            nodeid = str(node.id)
        else:
            global node_count
            nodeid = f"n{node_count}_{node.id}"
            node_count += 1
        return nodeid, [f"{nodeid} [shape=rectangle,label=\"{label}\"{extra_options}];"]
    elif node.is_decision():
        # Decision node
        shape_format = ",shape=circle,style=filled,fillcolor=gray95"
        visited.add(node)
        extra_options = ""
        if show_id:
            extra_options += (",xlabel=\"" + _format_sddnode_xlabel(node) + "\"")
        nodeid = str(node.id)
        s = [f"{nodeid} [label=\"{litnamemap.get('add', '+')}\"{shape_format}{extra_options}];"]
        # same_rank_nodes = []
        for idx, (prime, sub) in enumerate(node.elements()):
            prime_id, prime_s = _sddnode_to_dot_int(prime, visited, litnamemap, show_id, merge_leafs)
            sub_id, sub_s = _sddnode_to_dot_int(sub, visited, litnamemap, show_id, merge_leafs)
            ps_id = "ps_{}_{}".format(node.id, idx)
            s += [
                f"{ps_id} [label=\"{litnamemap.get('mult', '×')}\"{shape_format}{extra_options}];",
                "{} -> {} [arrowhead=none];".format(node.id, ps_id),
                "{} -> {} [arrowsize=.50,style=dashed];".format(ps_id, prime_id),
                "{} -> {} [arrowsize=.50];".format(ps_id, sub_id),
            ]
            s += prime_s
            s += sub_s
            # same_rank_nodes += [prime_id, sub_id]
        # s += ["{rank=same;" + ";".join(same_rank_nodes) + "};"]
        return nodeid, s


def vtree_to_dot(vtree, mgr, litnamemap=None, show_id=False):
    # type: (Vtree, SddManager, Optional[LitNameMap], bool) -> str
    """Generate (alternative) Graphviz DOT string for given Vtree.

    This method is an alternative to Vtree.dot().

    :param vtree: Vtree to plot
    :param mgr: SddManager associated with this Vtree
    :param litnamemap: Dictionary for node labels. For variable 1 the keys are 1 and -1 for positive and negative.
        For multiplication and addition the keys are 'mult' and 'add'. And for true and false, the keys are 'true'
        and 'false'.
    :param show_id: Show internal node ids, useful for debugging
    :return: String in the Graphviz DOT format
    """
    s = [
        "digraph vtree {"
    ]
    s += _vtree_to_dot_int(vtree, mgr, litnamemap, show_id)
    s += [
        "}"
    ]
    return "\n".join(s)


def _vtree_to_dot_int(vtree, mgr, litnamemap=None, show_id=False):
    # type: (Vtree, SddManager, Optional[LitNameMap], bool) -> List[str]
    s = []
    left = vtree.left()
    right = vtree.right()
    if left is None and right is None:
        name = vtree.var()
        if litnamemap is not None:
            name = litnamemap.get(name, name)
        extra_options = ""
        if show_id:
            extra_options += f",xlabel=\"{vtree.position()} (" +\
                             ",".join(litnamemap.get(node.literal, node.literal)
                                      for node in vtree.get_sdd_nodes(mgr)) +\
                             ")\""
        s += [f"{vtree.position()} [label=\"{name}\",shape=\"box\"{extra_options}];"]
    else:
        extra_options = ""
        if show_id:
            extra_options += f",xlabel=\"{vtree.position()} (" + \
                             ",".join(str(litnamemap.get(node.literal, node.literal))
                                      for node in vtree.get_sdd_nodes(mgr)) + \
                             ")\""
        s += [f"{vtree.position()} [shape=\"point\"{extra_options}];"]
    if left is not None:
        s += [f"{vtree.position()} -> {left.position()} [arrowhead=none];"]
        s += _vtree_to_dot_int(left, mgr, litnamemap, show_id)
    if right is not None:
        s += [f"{vtree.position()} -> {right.position()} [arrowhead=none];"]
        s += _vtree_to_dot_int(right, mgr, litnamemap, show_id)
    return s


def nnf_file_wmc(nnf_filename, weights=None):
    """Perform non-smoothed Weighted Model Counting on the given NNF file.

    This is an auxiliary function to perform WMC given an NNF file with only
    Python code. This function will thus also work, even if the C SDD library
    is not available.

    A typical NNF file looks like:

    nnf 12 12 3
    L 1
    ...
    A 2 3 9
    O 2 2 2 10

    """
    wmc = []  # type: List[Optional[float]]
    ln = 0
    detected_nnf = False
    true_weight = 1.0
    false_weight = 0.0
    with open(nnf_filename, 'r') as nnf_file:
        for line in nnf_file.readlines():
            cols = line.strip().split(' ')
            if cols[0] == 'c':
                continue
            if cols[0] == 'nnf':
                wmc = [None] * int(cols[1])
                detected_nnf = True
                continue
            if not detected_nnf:
                raise Exception(f"An NNF file should start with 'nnf'")
            if cols[0] == 'L':
                lit = int(cols[1])
                if lit in weights:
                    wmc[ln] = weights[lit]
                else:
                    wmc[ln] = true_weight
            if cols[0] == 'A':
                wmc[ln] = 1.0
                for i in range(int(cols[1])):
                    wmc[ln] *= wmc[int(cols[2 + i])]
            if cols[0] == 'O':
                wmc[ln] = false_weight
                for i in range(int(cols[2])):
                    wmc[ln] += wmc[int(cols[3 + i])]
            ln += 1
    return wmc[-1]


def sdd_file_wmc(sdd_filename, weights=None):
    """Perform non-smoothed Weighted Model Counting on the given SDD file.

    This is an auxiliary function to perform WMC given an SDD file with only
    Python code. This function will thus also work, even if the C SDD library
    is not available.

    A typical SDD file looks like:

    sdd 11
    L 1 0 1
    ...
    D 0 1 2 1 2 7 8
    """
    wmc = []  # type: List[Optional[float]]
    ln = 0
    detected_sdd = False
    true_weight = 1.0
    false_weight = 0.0
    with open(sdd_filename, 'r') as sdd_file:
        for line in sdd_file.readlines():
            cols = line.strip().split(' ')
            if cols[0] == 'c':
                continue
            if cols[0] == 'sdd':
                detected_sdd = True
                wmc = [None] * int(cols[1])
                continue
            if not detected_sdd:
                raise Exception(f"An SDD file should start with 'sdd'")
            if cols[0] == 'L':
                nodeid = int(cols[1])
                lit = int(cols[3])
                if lit in weights:
                    wmc[nodeid] = weights[lit]
                else:
                    wmc[nodeid] = 1.0
            if cols[0] == 'F':
                nodeid = int(cols[1])
                wmc[nodeid] = false_weight
            if cols[0] == 'T':
                nodeid = int(cols[1])
                wmc[nodeid] = true_weight
            if cols[0] == 'D':
                nodeid = int(cols[1])
                nb_elmts = int(cols[3])
                elmts = [int(col) for col in cols[4:]]
                w = 0.0
                for idx in range(nb_elmts):
                    w += wmc[elmts[2 * idx]] * wmc[elmts[2 * idx + 1]]
                wmc[nodeid] = w
            ln += 1
    return wmc[0]


def psdd_file_wmc(psdd_filename, observations=None):
    """Perform Weighted Model Counting on the given PSDD file.

    This is an auxiliary function to perform WMC given a PSDD file with only
    Python code. This function will thus also work, even if the C SDD library
    is not available.

    A typical PSDD file looks like (Yitao's version):

    c ids of psdd nodes start at 0
    c psdd nodes appear bottom-up, children before parents
    c
    c file syntax:
    c psdd count-of-sdd-nodes
    c L id-of-literal-sdd-node id-of-vtree literal
    c T id-of-trueNode-sdd-node id-of-vtree variable log(litProb)
    c D id-of-decomposition-sdd-node id-of-vtree number-of-elements {id-of-prime id-of-sub log(elementProb)}*
    psdd 49
    T 0 20 11 -0.6931471805599453

    :return: log(WMC)
    """
    wmc = []  # type: List[Optional[float]]
    ln = 0
    detected_psdd = False
    with open(psdd_filename, 'r') as sdd_file:
        for line in sdd_file.readlines():
            cols = line.strip().split(' ')
            if cols[0] == 'c':
                continue
            if cols[0] == 'psdd':
                detected_psdd = True
                wmc = [None] * int(cols[1])
                continue
            if not detected_psdd:
                raise Exception(f"An SDD file should start with 'sdd'")
            if cols[0] == 'L':
                nodeid = int(cols[1])
                lit = int(cols[2])
                if observations is not None and lit in observations:
                    if var > 0:
                        wmc[nodeid] = 0.0 if observations[lit] else -math.inf
                    else:
                        wmc[nodeid] = 0.0 if not observations[lit] else -math.inf
                else:
                    wmc[nodeid] = 0.0
            if cols[0] == 'F':
                raise Exception("There should be no false nodes")
                # nodeid = int(cols[1])
                # wmc[nodeid] = -math.inf
            if cols[0] == 'T':
                nodeid, vtreeid, lit = [int(val) for val in cols[1:4]]
                var = abs(lit)
                theta = float(cols[4])
                if observations is not None and var in observations:
                    if lit > 0:
                        logprob = 0.0 if observations[var] else -math.inf
                    else:
                        logprob = 0.0 if not observations[var] else -math.inf
                else:
                    logprob = theta
                wmc[nodeid] = logprob
            if cols[0] == 'D':
                nodeid, vtree_id, nb_elmts = [int(val) for val in cols[1:4]]
                elmts = cols[4:]
                w = -math.inf
                for idx in range(nb_elmts):
                    p, s, t = elmts[3 * idx: 3 * idx + 3]
                    wmc_p = wmc[int(p)]
                    wmc_s = wmc[int(s)]
                    theta = float(s)
                    add = wmc_p + wmc_s + theta
                    if math.isinf(w) and w < 0:
                        w = add
                    elif math.isinf(add) and add < 0:
                        pass
                    elif w < add:
                        w = add + math.log1p(math.exp(w - add))
                    else:
                        w = w + math.log1p(math.exp(add - w))
                wmc[nodeid] = w
            ln += 1
    return wmc[0]


class BitArray:
    def __init__(self, size, fill=0):
        """Array of boolean values.

        Based on https://wiki.python.org/moin/BitArrays

        :param size: Length of array
        :param fill: Default value to set. Should be 0 or 1.
        """
        int_size = size >> 5  # number of 32 bit integers
        if size & 31:  # if bitSize != (32 * n) add
            int_size += 1  # a record for stragglers
        if fill == 1:
            fill = 4294967295  # all bits set
        else:
            fill = 0  # all bits cleared

        self.bits = array.array('I')  # 'I' = unsigned 32-bit integer
        self.bits.extend((fill,) * int_size)

    def is_set(self, bit_num):
        """Returns a nonzero result, 2**offset, if the bit at 'bit_num' is set to 1."""
        record = bit_num >> 5
        offset = bit_num & 31
        mask = 1 << offset
        return self.bits[record] & mask > 0

    def __getitem__(self, item):
        return self.is_set(item)

    def set(self, bit_num):
        """Set the bit at 'bit_num' to 1."""
        record = bit_num >> 5
        offset = bit_num & 31
        mask = 1 << offset
        self.bits[record] |= mask

    def __setitem__(self, key, value):
        if value == 0:
            self.clear(key)
        elif value == 1:
            self.set(key)
        else:
            raise ValueError("Key should be 0 or 1")

    def clear(self, bit_num):
        """Clear the bit at 'bit_num'."""
        record = bit_num >> 5
        offset = bit_num & 31
        mask = ~(1 << offset)
        self.bits[record] &= mask

    def toggle(self, bit_num):
        """Invert the bit at 'bit_num', 0 -> 1 and 1 -> 0."""
        record = bit_num >> 5
        offset = bit_num & 31
        mask = 1 << offset
        self.bits[record] ^= mask

    def __str__(self):
        s = ""
        for bits in self.bits:
            s += "{0:032b}".format(bits)
        return s
