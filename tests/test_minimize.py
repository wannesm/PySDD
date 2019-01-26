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


def test_min1():
    vtree = Vtree(var_count=4, var_order=[1, 4, 2, 3], vtree_type="right")
    sdd = SddManager.from_vtree(vtree)
    sdd.auto_gc_and_minimize_off()
    a, b, c, d = sdd.vars
    f = ((a & b) | (c & d))
    f.ref()
    if directory:
        with (directory / "vtree1_before.gv").open("w") as out:
            print(sdd.vtree().dot(), file=out)
        with (directory / "sdd1_before.gv").open("w") as out:
            print(f.dot(), file=out)
    result = sdd.minimize()
    print(result)
    if directory:
        with (directory / "vtree2_after.gv").open("w") as out:
            print(sdd.vtree().dot(), file=out)
        with (directory / "sdd1_after.gv").open("w") as out:
            print(f.dot(), file=out)
    f.deref()

    wmc = f.wmc(log_mode=False)
    mc = wmc.propagate()
    # print(f"mc = {mc}")
    assert mc == 7.0


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_min1()
