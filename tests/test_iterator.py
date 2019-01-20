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
        with (directory / "sdd.gv").open("w") as out:
            print(f.dot2(), file=out)
        with (directory / "vtree.gv").open("w") as out:
            print(sdd.vtree().dot2(), file=out)

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


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_it1()
