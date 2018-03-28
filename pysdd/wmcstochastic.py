"""
stochasticcomputing.py - Apply stochastic computing to SDD

__author__ = "Wannes Meert"
__license__ = "APL"

"""
import random
from itertools import accumulate

from .sdd import WmcManager


class WmcStochastic(WmcManager):

    def propagate_normal(self):
        return self.depth_first_normal(self.node)

    def depth_first_normal(self, node):
        # TODO: This ignores smoothing
        if node.is_decision():
            rvalue = 0
            for prime, sub in node.elements():
                # Conjunction
                result = self.depth_first_normal(prime) * self.depth_first_normal(sub)
                # Disjunction
                rvalue += result
        elif node.is_true():
            rvalue = self.one_weight
        elif node.is_false():
            rvalue = self.zero_weight
        elif node.is_literal():
            rvalue = self.literal_weight(node)
        else:
            raise Exception(f"Unknown node type: {node}")
        return rvalue

    def propagate(self, bitlength=100):
        nb_pos, nb_neg = 0, 0
        scaling = 0
        for i in range(bitlength):
            value, scaling = self.depth_first(self.node)
            if value:
                nb_pos += 1
            else:
                nb_neg += 1
        return (nb_pos / (nb_pos + nb_neg)) * scaling

    def depth_first(self, node):
        # TODO: This ignores smoothing
        if node.is_decision():
            rvalues = []
            rcounts = []
            for prime, sub in node.elements():
                # Conjunction
                pw, pc = self.depth_first(prime)
                sw, sc = self.depth_first(sub)
                result_value = pw & sw
                result_count = pc * sc
                # Disjunction
                rvalues.append(result_value)
                rcounts.append(result_count)
            rcount = sum(rcounts)
            randval = random.random()
            choice = None
            for i, cw in enumerate(accumulate(w / rcount for w in rcounts)):
                if cw > randval:
                    choice = i
                    break
            if choice is None:
                choice = len(rcounts) - 1
            # print(randval, rcounts, choice)
            rvalue = (rvalues[choice], rcount)
        elif node.is_true():
            rvalue = (True, 1)
        elif node.is_false():
            rvalue = (False, 1)
        elif node.is_literal():
            w = self.literal_weight(node)
            if w > 1.0:
                raise Exception(f"Stochastic WMC expects probabilities as weights, got {w} for {node}.")
            randval = random.random()
            if randval < w:
                rvalue = (True, 1)
            else:
                rvalue = (False, 1)
            # print(f'literal {node:<11}: weight={w}, random={randval:.3f}, result={rvalue}')
        else:
            raise Exception(f"Unknown node type: {node}")
        return rvalue

