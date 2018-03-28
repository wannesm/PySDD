from pysdd.sdd import SddManager, Vtree, WmcManager
from pysdd.wmcstochastic import WmcStochastic
import pytest
from array import array


def test_wmc1(verbose=False):
    vtree = Vtree(var_count=4, var_order=[2, 1, 4, 3], vtree_type="balanced")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = [sdd.literal(i) for i in range(1, 5)]
    # formula = (a & b) | c
    formula = (a & b) | (b & c) | (c & d)
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


if __name__ == "__main__":
    test_wmc1(verbose=True)
