from pysdd.sdd import SddManager, Vtree
from pysdd.iterator import SddIterator
from pysdd.io import sdd_to_dot, vtree_to_dot
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
        litnamemap = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
        for key, val in list(litnamemap.items()):
            litnamemap[-key] = f"¬{val}"
        with (directory / "sdd1.gv").open("w") as out:
            print(f.dot(), file=out)
        with (directory / "sdd2.gv").open("w") as out:
            print(sdd_to_dot(f, litnamemap=litnamemap, show_id=True), file=out)
        with (directory / "vtree1.gv").open("w") as out:
            print(sdd.vtree().dot(), file=out)
        with (directory / "vtree2.gv").open("w") as out:
            print(vtree_to_dot(sdd.vtree(), litnamemap=litnamemap, show_id=True), file=out)

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 7.0

    it = SddIterator(sdd, smooth=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 7, "MC {} != 7".format(mc)

    it = SddIterator(sdd, smooth=False)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 3, "MC (non-smooth) {} != 3".format(mc)


def test_it2():
    """ Test case where formula = True """
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = sdd.vars[:5]
    f = (a | -a)  # = SddNode(True)

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 16.0

    it = SddIterator(sdd, smooth=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 16, "MC {} != 16".format(mc)

    it = SddIterator(sdd, smooth=False)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 1, "MC (non-smooth) {} != 1".format(mc)


def test_it3():
    """ Test case where formula = literal """
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = sdd.vars[:5]
    f = a  # = SddNode(True)

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 8.0

    it = SddIterator(sdd, smooth=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 8, "MC {} != 8".format(mc)

    it = SddIterator(sdd, smooth=False)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 1, "MC (non-smooth) {} != 1".format(mc)

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_it1()
    test_it2()
    test_it3()
