"""
iterator - SDD

__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

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

