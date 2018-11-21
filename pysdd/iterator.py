# -*- coding: UTF-8 -*-
"""
pysdd.iterator
~~~~~~~~~~~~~~

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2018 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
from collections import deque


class SddIterator:
    def __init__(self, sdd, smooth=True, cache=True):
        """Iterate over the SDD graph.

        Supports smoothing: An arithmetic circuit AC(X) is smooth iff
        (1) it contains at least one indicator for each variable in X, and
        (2) for every child c of '+'-node n, we have vars(n) = vars(c).

        :param sdd: WmcManager
        :param smooth: Perform smoothing while iterating over the graph
        :param cache: Cache visited nodes
        """
        self.sdd = sdd
        self.cache = cache
        self._cache = None
        self.smooth = smooth

    def depth_first(self, node, func):
        """Depth first iterator

        :param node: Start node
        :param func: Function to be called for each node:
        ``rvalue = func(node, [(prime, sub, variables)], variables)``
        :return:
        """
        self._cache = {} if self.cache else None
        return self.depth_first_rec(node, func)

    def depth_first_rec(self, node, func):

        # print(f">{node}")
        if self._cache is not None and node in self._cache:
            # print(f"<{node}: From cache: {self.cache[node]}")
            return self._cache[node]
        variables = set() if self.smooth else None
        if node.is_decision():
            rvalues = []
            for prime, sub in node.elements():
                # Conjunction
                # result = self.depth_first(prime, func) * self.depth_first(sub, func)
                # Disjunction
                # rvalue += result
                prime, prime_vars = self.depth_first_rec(prime, func)
                sub, sub_vars = self.depth_first_rec(sub, func)
                if self.smooth:
                    prime_vars.update(sub_vars)
                    variables.update(prime_vars)
                else:
                    prime_vars = None
                rvalues.append((prime, sub, prime_vars))
            rvalue = func(node, rvalues, variables)
        else:
            if self.smooth and node.is_literal():
                variables.add(abs(node.literal))
            rvalue = func(node, None, variables)
        if self._cache is not None:
            self._cache[node] = (rvalue, variables)
        # print(f"<{node}: Computed: ({rvalue},{variables})")
        return rvalue, variables

    @staticmethod
    def func_modelcounting(node, rvalues, all_variables):
        """Method to pass on to ``depth_first`` to perform model counting."""
        if rvalues is None:
            # Leaf
            if node.is_true():
                return 1
            elif node.is_false():
                return 0
            elif node.is_literal():
                return 1
            else:
                raise Exception("Unknown leaf type for node {}".format(node))
        else:
            # Decision node
            if not node.is_decision():
                raise Exception("Expected a decision node for node {}".format(node))
            rvalue = 0
            for prime, sub, variables in rvalues:
                variables = all_variables - variables
                smooth_factor = 2**len(variables)
                rvalue += prime * sub * smooth_factor
            return rvalue
