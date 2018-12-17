from pysdd.sdd import SddManager, Vtree
from pysdd.iterator import SddIterator
import sys
import os
import logging
from pathlib import Path


logger = logging.getLogger("pysdd")
directory = None
counter = 0


def test_it1():
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = sdd.vars[:5]
    f = ((a & b) | (c & d))
    if directory:
        dot_fn = directory / "sdd.dot"
        with dot_fn.open("w") as out:
            print(f.dot(), file=out)

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 7.0

    global counter
    counter = 0

    def func(node, rvalues, all_variables):
        global counter
        counter += 1
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

    it = SddIterator(sdd, smooth=True, cache=False)
    mc, _variables = it.depth_first(f, func)
    # print(f"mc = {mc}")
    assert mc == 7, f"Expected 7 != {mc}"
    # print(f"Counter = {counter}")
    assert counter == 17

    counter = 0
    it = SddIterator(sdd, smooth=True, cache=True)
    mc, _variables = it.depth_first(f, func)
    # print(f"mc = {mc}")
    assert mc == 7
    # print(f"Counter = {counter}")
    assert counter == 12, "Visited nodes {} != 12".format(counter)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_it1()
