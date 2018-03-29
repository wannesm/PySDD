from pysdd.sdd import SddManager, Vtree, WmcManager
from pysdd.wmcstochastic import WmcStochastic
import pytest
from array import array
import random


def test_wmc1(verbose=False):
    vtree = Vtree(var_count=4, var_order=[2, 1, 4, 3], vtree_type="balanced")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = [sdd.literal(i) for i in range(1, 5)]
    # formula = (a & b) | c
    formula = (a & b) | (b & c) | (c & d)
    if verbose:
        with open("sdd.dot", "w") as out:
            print(formula.dot(), file=out)

    #                     -d   -c   -b   -a   a    b    c    d
    weights = array('d', [0.8, 0.7, 0.6, 0.5, 0.5, 0.4, 0.3, 0.2])

    # Normal WMC
    wmc = WmcManager(formula, log_mode=False)
    print(f"MC = {wmc.propagate()}")
    wmc.set_literal_weights_from_array(weights)
    wmc_result = wmc.propagate()
    print(f"WMC-Normal = {wmc_result}")

    # Stochastic WMC
    wmcs = WmcStochastic(formula, log_mode=False)
    wmcs.set_literal_weights_from_array(weights)
    wmcs_result = wmcs.propagate(bitlength=1000)
    print(f"WMC-Stochastic = {wmcs_result}")

    # assert wmc_result == pytest.approx(wmcs_result)


@pytest.mark.skip(reason="Takes too long to generate the figure and is the same test as test_wmc1")
def test_wmc2(verbose=False):
    vtree = Vtree(var_count=4, var_order=[2, 1, 4, 3], vtree_type="balanced")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = [sdd.literal(i) for i in range(1, 5)]
    # formula = (a & b) | c
    formula = (a & b) | (b & c) | (c & d)

    #                     -d   -c   -b   -a   a    b    c    d
    weights = array('d', [0.8, 0.7, 0.6, 0.5, 0.5, 0.4, 0.3, 0.2])

    # Normal WMC
    wmc = WmcManager(formula, log_mode=False)
    wmc.set_literal_weights_from_array(weights)
    wmc_result = wmc.propagate()

    # Stochastic WMC
    wmcs = WmcStochastic(formula, log_mode=False)
    wmcs.set_literal_weights_from_array(weights)
    nb_pos, nb_neg, scaling = 0, 0, 1
    wmcs_results = []
    iterations = 1000
    for i in range(iterations):
        random.seed()
        nb_pos_i, nb_neg_i, scaling_i = wmcs.propagate_counts(bitlength=10)
        nb_pos += nb_pos_i
        nb_neg += nb_neg_i
        scaling = scaling_i
        wmcs_results.append((nb_pos / (nb_pos + nb_neg)) * scaling)
    print(wmcs_results[-1])
    if verbose:
        import matplotlib.pyplot as plt
        plt.plot([i*10 for i in range(iterations)], [wmc_result]*iterations)
        plt.plot([i*10 for i in range(iterations)], wmcs_results)
        plt.savefig("stochastic_wmc.png")


if __name__ == "__main__":
    test_wmc2(verbose=True)
