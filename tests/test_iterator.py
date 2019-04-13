from pysdd.sdd import SddManager, Vtree
from pysdd.iterator import SddIterator
from pysdd.util import sdd_to_dot, vtree_to_dot
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
            print(vtree_to_dot(sdd.vtree(), sdd, litnamemap=litnamemap, show_id=True), file=out)
    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 7.0

    it = SddIterator(sdd, smooth=True, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 7, "MC {} != 7".format(mc)

    it = SddIterator(sdd, smooth=False, smooth_to_root=True)
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

    it = SddIterator(sdd, smooth=True, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 16, "MC {} != 16".format(mc)

    it = SddIterator(sdd, smooth=False, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 1, "MC (non-smooth) {} != 1".format(mc)

    f = (a & -a)  # = SddNode(False)

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 0.0

    it = SddIterator(sdd, smooth=True, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 0, "MC {} != 0".format(mc)

    it = SddIterator(sdd, smooth=False, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 0, "MC (non-smooth) {} != 0".format(mc)


def test_it3():
    """ Test case where formula = literal or -literal """
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = sdd.vars[:5]
    f = a

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 8.0

    it = SddIterator(sdd, smooth=True, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 8, "MC {} != 8".format(mc)

    it = SddIterator(sdd, smooth=False, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 1, "MC (non-smooth) {} != 1".format(mc)

    f = -a

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 8.0

    it = SddIterator(sdd, smooth=True, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 8, "MC {} != 8".format(mc)

    it = SddIterator(sdd, smooth=False, smooth_to_root=True)
    mc = it.depth_first(f, SddIterator.func_modelcounting)
    assert mc == 1, "MC (non-smooth) {} != 1".format(mc)


def test_it4():
    vtree = Vtree(var_count=4, var_order=[4, 3, 2, 1], vtree_type="right")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = sdd.vars
    f1 = a | b
    f2 = f1 | c
    f3 = f2 | d
    f1.ref()
    f2.ref()
    f3.ref()

    if directory:
        litnamemap = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
        for key, val in list(litnamemap.items()):
            litnamemap[-key] = f"¬{val}"
        with (directory / "sdd.gv").open("w") as out:
            print(sdd_to_dot(f3, litnamemap=litnamemap, show_id=True), file=out)
        with (directory / "vtree.gv").open("w") as out:
            print(vtree_to_dot(sdd.vtree(), litnamemap=litnamemap, show_id=True), file=out)

    it = SddIterator(sdd, smooth=True)
    mc = it.depth_first(f1, SddIterator.func_modelcounting)
    assert mc == 3, "MC {} != 3".format(mc)

    it = SddIterator(sdd, smooth=True, smooth_to_root=True)
    mc = it.depth_first(f1, SddIterator.func_modelcounting)
    assert mc == 12, "MC {} != 3 * 2**2 = 12".format(mc)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_it1()
    # test_it2()
    # test_it3()
    # test_it4()
