# -*- coding: UTF-8 -*-
"""
pysdd.iterator
~~~~~~~~~~~~~~

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2019 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
from collections import deque
from .sdd import SddManager, Vtree, SddNode
from .util import BitArray

MYPY = False
if MYPY:
    from typing import Dict, Set, Optional, List, Tuple, Callable, Union


class SddIterator:
    def __init__(self, sdd, smooth=True, smooth_to_root=False):
        """Simple iterator to iterate over the SDD graph.

        Supports smoothing: An arithmetic circuit AC(X) is smooth iff
        (1) it contains at least one indicator for each variable in X, and
        (2) for every child c of '+'-node n, we have vars(n) = vars(c).

        Note, if you know that you will be performing WMC, smoothing can be implemented more efficient
        by keeping track of the expected WMC of used and unused variables in the vtree instead of keeping
        track of the sets of variables as is done in this iterator.

        :param sdd: WmcManager
        :param smooth: Perform smoothing while iterating over the graph
        :param smooth_to_root: Perform smoothing wrt root instead of a given node
        """
        self.sdd = sdd  # type: SddManager
        self.vtree = sdd.vtree()  # type: Vtree
        self._wmc_cache = dict()  # type: Dict[SddNode, Union[float, int]]
        # Map Vtree node positions to expected variables
        self._expected_vars = None  # type: Optional[Dict[int, Set[int]]]
        # Map Sdd nodes to missing variables
        self._missing_vars = dict()  # type: Dict[SddNode, Set[int]]
        self.smooth = smooth  # type: bool
        self.smooth_to_root = smooth_to_root  # type: bool

        if self.smooth:
            self._cache_expected_vars()

    def _cache_expected_vars(self):
        self._expected_vars = dict()
        nb_vtree_nodes = self.sdd.var_count() * 2 - 1
        # visited = [False] * nb_vtree_nodes
        visited = BitArray(nb_vtree_nodes)
        queue = deque([self.vtree])
        while len(queue) > 0:
            node = queue.pop()  # type: Vtree
            pos = node.position()
            if node.is_leaf():
                self._expected_vars[pos] = {node.var()}
            else:
                if visited[pos]:
                    self._expected_vars[pos] = self._expected_vars[node.left().position()] | \
                                               self._expected_vars[node.right().position()]
                else:
                    visited[pos] = True
                    queue.append(node)
                    queue.append(node.right())
                    queue.append(node.left())

    def depth_first_from_root(self, func):
        # type: (SddIterator, Callable) -> List[Union[int, float]]
        """Depth first iterator starting from the root nodes.

        See `depth_first` for more details.
        """
        results = []
        for node in self.vtree.get_sdd_rootnodes(self.sdd):
            results.append(self.depth_first(node, func))
        return results

    def depth_first(self, node, func):
        # type: (SddIterator, SddNode, Callable) -> Union[int, float]
        """Depth first iterator

        :param node: Start node
        :param func: Function to be called for each node:
        ``rvalue = func(node, [(prime_rvalue, sub_rvalue, prime_vars, sub_vars)],
                        expected_prime_vars, expected_sub_vars)``
          The given arguments are:
          * node: Current node, if None, it should be considered a decision node
          * prime_rvalue: Return value from prime node
          * sub_rvalue: Return value from sub node
          * prime_vars: Variables present in prime
          * sub_vars: Variables present in sub
          * expected_prime_vars: Variables that are expected in prime
          * expected_sub_vars: Variables that are expected in sub
          The return value can be any type, there are no assumptions.
          For WMC this is typically float, and for MC int.
        :return:
        """
        self._wmc_cache = dict()
        if self.smooth and self._expected_vars is None:
            self._cache_expected_vars()
        if self.smooth and (node.is_true() or node.is_literal()):
            wmc = func(node, None, self._expected_vars[self.vtree.position()], set())
        else:    
            wmc = self.depth_first_rec(node, func)
        if self.smooth_to_root and not (node.is_true() or node.is_literal() or node.is_false()):
            root = self.vtree.root()
            if root != node.vtree():
                wmc_prime = wmc
                wmc_sub = func(self.sdd.true(), None, None, None)
                used_prime_vars = self._expected_vars[node.vtree().position()]
                used_sub_vars = set()
                rvalues = [(wmc_prime, wmc_sub, used_prime_vars, used_sub_vars)]
                expected_prime_vars = used_prime_vars
                expected_sub_vars = self._expected_vars[root.position()] - used_prime_vars
                wmc = func(None, rvalues, expected_prime_vars, expected_sub_vars)
        return wmc

    def depth_first_rec(self, node, func):
        # type: (SddIterator, SddNode, Callable) -> Union[int, float]
        if node in self._wmc_cache:
            return self._wmc_cache[node]
        if node.is_false():
            result = func(node, None, None, None)
            self._wmc_cache[node] = result
            return result
        if node.is_true():
            result = func(node, None, None, None)
            self._wmc_cache[node] = result
            return result
        vtree = node.vtree()
        if node.is_decision():
            rvalues = []
            vtree_left = vtree.left()
            if not self.smooth or vtree_left is None:
                expected_prime_vars = set()
            else:
                expected_prime_vars = self._expected_vars[vtree_left.position()]
            vtree_right = vtree.right()
            if not self.smooth or vtree_right is None:
                expected_sub_vars = set()
            else:
                expected_sub_vars = self._expected_vars[vtree_right.position()]
            for prime, sub in node.elements():
                wmc_prime = self.depth_first_rec(prime, func)
                wmc_sub = self.depth_first_rec(sub, func)
                if not self.smooth:
                    used_prime_vars = None
                    used_sub_vars = None
                else:
                    if prime.vtree() is None:
                        used_prime_vars = set()
                    else:
                        used_prime_vars = self._expected_vars[prime.vtree().position()]
                    if sub.vtree() is None:
                        used_sub_vars = set()
                    else:
                        used_sub_vars = self._expected_vars[sub.vtree().position()]
                rvalues.append((wmc_prime, wmc_sub, used_prime_vars, used_sub_vars))
            rvalue = func(node, rvalues, expected_prime_vars, expected_sub_vars)
        else:
            rvalue = func(node, None, None, None)
        if self._wmc_cache is not None:
            self._wmc_cache[node] = rvalue
        return rvalue

    @staticmethod
    def func_modelcounting(node, rvalues, expected_prime_vars, expected_sub_vars):
        # type: (SddNode, List[Tuple[int, int, Set[int], Set[int]]], Set[int], Set[int]) -> int
        """Method to pass on to ``depth_first`` to perform model counting.

        Note that the WmcManager method to perform WMC is much more efficient, and supports weights.
        """
        if rvalues is None:
            # Leaf
            if node.is_true():
                prime_smooth_factor = 2**len(expected_prime_vars) if expected_prime_vars is not None else 1
                sub_smooth_factor = 2**len(expected_sub_vars) if expected_sub_vars is not None else 1
                return prime_smooth_factor * sub_smooth_factor

            elif node.is_false():
                return 0

            elif node.is_literal():
                if expected_prime_vars is not None:
                    nb_missing_vars = len(expected_prime_vars)
                    if abs(node.literal) in expected_prime_vars:
                        nb_missing_vars -= 1

                    prime_smooth_factor = 2**nb_missing_vars
                else:
                    prime_smooth_factor = 1

                if expected_sub_vars is not None:
                    nb_missing_vars = len(expected_sub_vars)
                    if abs(node.literal) in expected_sub_vars:
                        nb_missing_vars -= 1
                    sub_smooth_factor = 2**nb_missing_vars
                else:
                    sub_smooth_factor = 1

                return prime_smooth_factor * sub_smooth_factor
            else:
                raise Exception("Unknown leaf type for node {}".format(node))
        else:
            # Decision node
            if node is not None and not node.is_decision():
                raise Exception("Expected a decision node for node {}".format(node))
            rvalue = 0
            for mc_prime, mc_sub, prime_vars, sub_vars in rvalues:
                if prime_vars is not None:
                    nb_missing_vars = len(expected_prime_vars) - len(prime_vars)
                    prime_smooth_factor = 2**nb_missing_vars
                else:
                    prime_smooth_factor = 1
                if sub_vars is not None:
                    nb_missing_vars = len(expected_sub_vars) - len(sub_vars)
                    sub_smooth_factor = 2**nb_missing_vars
                else:
                    sub_smooth_factor = 1
                rvalue += mc_prime * prime_smooth_factor * mc_sub * sub_smooth_factor
            return rvalue
