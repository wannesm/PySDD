"""
iterator - SDD

__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

"""

class SddIterator:
    def __init__(self, sdd):
        self.sdd = sdd

    def depth_first(self, node, func):
            rvalue = func(node)
        for prime, sub in node.elements():
            rvalue += self.depth_first(prime, func)
            rvalue += self.depth_first(sub, func)
        return rvalue

