# -*- coding: UTF-8 -*-
"""
pysdd.iterator
~~~~~~~~~~~~~~

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2018 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
class SddIterator:
    def __init__(self, sdd):
        self.sdd = sdd

    def depth_first(self, node, func):
        if node.is_decision():
            rvalue = 0
            for prime, sub in node.elements():
                # Conjunction
                result = self.depth_first(prime, func) * self.depth_first(sub, func)
                # Disjunction
                rvalue += result
        else:
            rvalue = func(node)
        return rvalue

