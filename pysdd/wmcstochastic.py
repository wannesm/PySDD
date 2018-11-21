# -*- coding: UTF-8 -*-
"""
pysdd.wmcstochastic
~~~~~~~~~~~~~~~~~~~

Apply stochastic computing to Sentential Decision Diagrams (SDD).

:author: Wannes Meert
:copyright: Copyright 2018 KU Leuven.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import random
from itertools import accumulate

from .sdd import WmcManager


class WmcStochastic(WmcManager):
    """Weighted Model Counting using Stochastic Computing and a Sentential Decision Diagram (SDD).

    This is an example implementation on how you can write your own custom Weighted Model Counting
    algorithm on top of the PySDD library.

    This class is a demonstration how stochastic computing [1,2] could be used for weighted model counting
    given an SDD datastructure. The basic concept is that instead of propagating floating point numbers
    through the SDD, only True and False samples are passed through. Each leaf generates samples from
    a Bernouilli distribution with as parameter the probability associated, the samples collected at the
    root node then represent a Bernouilli distribution with as mean the Weighted Model Count.

    The main change is that a conjunction or multiplication is replaced with an AND gate and a
    disjunction or addition is replaced with a MUX gate. Since a MUX gate rescales the result of
    the addition back to the range [0,1], we need to keep track of scaling factors to tune the MUX
    gates in the network.

    While Stochastic Computing has some advantages, like small circuit surface, cheap hardware, and
    robust against noise, it also has some significant disadvantages. For high precision computation
    it needs an exponential large number of bits (2^n for an n-bit binary number) and the random
    number generator is expensive.

    [1] Von Neumann, John. "Probabilistic logics and the synthesis of reliable organisms from unreliable
    components." Automata studies 34 (1956): 43-98.
    [2] A. Alaghi and J. P. Hayes. Computing with randomness. IEEE Spectrum, (3), March 2018.
    """

    def __init__(self, node, log_mode=1):
        super().__init__(node, log_mode)
        self.cache = dict()
        self.scalings = dict()
        self.or_cumweights = dict()
        self.compute_scalings()

    def propagate_normal(self):
        """Comparison to normal weighted model counting given an SDD.

        Note that this simple example does not perform smoothing and will thus not
        return a correct result for non-smoothed SDDs. For a correct weighted model
        counter smoothing should also be implemented.
        """
        return self.depth_first_normal(self.node)

    def depth_first_normal(self, node):
        """Depth first search to compute the WMC.

        This does not yet perform smoothing!
        """
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
        """Weighted Model Counting using Stochastic Computation."""
        nb_pos, nb_neg, scaling = self.propagate_counts(bitlength)
        return (nb_pos / (nb_pos + nb_neg)) * scaling

    def propagate_counts(self, bitlength=100):
        nb_pos, nb_neg = 0, 0
        scaling = self.scalings[self.node.id]
        for i in range(bitlength):
            if self.counting_df(self.node):
                nb_pos += 1
            else:
                nb_neg += 1
        return nb_pos, nb_neg, scaling

    def counting_df(self, node):
        """Depth-first counting using Stochastic Computing.

        Missing from this example to enable a full features WMC:
        - Smoothing should be included.
        - Subtrees that always have zero or one as values should be pruned to increase the resolution.
        """
        self.cache = dict()
        return self.counting_df_rec(node)

    def counting_df_rec(self, node):
        if node in self.cache:
            return self.cache[node]
        if node.is_decision():
            rcounts = []
            for prime, sub in node.elements():
                # Conjunction
                count_p = self.counting_df(prime)
                count_s = self.counting_df(sub)
                result_count = count_p & count_s
                rcounts.append(result_count)
            # Disjunction
            cumweights = self.or_cumweights[node.id]
            randval = random.random()
            choice = None
            for i, cw in enumerate(cumweights):
                if cw > randval:
                    choice = i
                    break
            if choice is None:
                choice = len(rcounts) - 1
            rvalue = rcounts[choice]
        elif node.is_true():
            rvalue = True
        elif node.is_false():
            rvalue = False
        elif node.is_literal():
            w = self.literal_weight(node)
            if w > 1.0:
                raise Exception(f"Stochastic WMC expects probabilities as weights, got {w} for {node}.")
            randval = random.random()
            if randval < w:
                rvalue = True
            else:
                rvalue = False
        else:
            raise Exception(f"Unknown node type: {node}")
        self.cache[node] = rvalue
        return rvalue

    def compute_scalings(self):
        """Compute all the scaling factors.

        This is a pre-processing step to set up the scaling necessary to make the MUX gates compute
        correct results. This is similar to the scaling operations that are also required for
        performing computations with fixed-point integers
        (https://en.wikipedia.org/wiki/Fixed-point_arithmetic#Operations).
        """
        self.cache = dict()
        self.compute_scalings_df(self.node)

    def compute_scalings_df(self, node):
        """Computing all the scaling factors using depth-first search."""
        if node in self.cache:
            return self.cache[node]
        if node.is_decision():
            scalings = []
            for prime, sub in node.elements():
                # Conjunction
                scaling_p = self.compute_scalings_df(prime)
                scaling_s = self.compute_scalings_df(sub)
                result_scaling = scaling_p * scaling_s
                scalings.append(result_scaling)
            # Disjunction
            total_scaling = sum(scalings)
            self.or_cumweights[node.id] = list(accumulate(s / total_scaling for s in scalings))
            self.scalings[node.id] = total_scaling
            rvalue = total_scaling
        elif node.is_true():
            self.scalings[node.id] = 1
            rvalue = 1
        elif node.is_false():
            self.scalings[node.id] = 1
            rvalue = 1
        elif node.is_literal():
            self.scalings[node.id] = 1
            rvalue = 1
        else:
            raise Exception(f"Unknown node type: {node}")
        self.cache[node] = rvalue
        return rvalue
