from pysdd.sdd import SddManager, Vtree
from pysdd.iterator import SddIterator
import sys
import os
import logging
from pathlib import Path


logger = logging.getLogger("pysdd")
directory = None
counter = 0


def test_dot():
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    if directory is not None:
        with (directory / "vtree1.gv").open("w") as ofile:
            s = vtree.dot()
            print(s, file=ofile)
        with (directory / "vtree2.gv").open("w") as ofile:
            s = vtree.dot2()
            print(s, file=ofile)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_dot()
