from pysdd.util import nnf_file_wmc, sdd_file_wmc
import sys
import os
import logging
from pathlib import Path


logger = logging.getLogger("pysdd")
directory = None
counter = 0
here = Path(__file__).parent


def test_nnf1():
    weights = {
        +3: 0.5, +2: 0.5, +1: 1,
        -3: 0.5, -2: 0.5, -1: 1
    }
    wmc = nnf_file_wmc(here / "rsrc" / "test.cnf.nnf", weights)
    assert wmc == 1.0


def test_nnf2():
    weights = {
        +3: 0.5, +2: 0.5, +1: 1,
        -3: 0.5, -2: 0.5, -1: 0
    }
    wmc = nnf_file_wmc(here / "rsrc" / "test.cnf.nnf", weights)
    assert wmc == 0.75


def test_sdd1():
    weights = {
        +3: 0.5, +2: 0.5, +1: 1,
        -3: 0.5, -2: 0.5, -1: 1
    }
    wmc = sdd_file_wmc(here / "rsrc" / "test.sdd", weights)
    print("WMC", wmc)
    assert wmc == 1.0, f"{wmc} != 1.0"


def test_sdd2():
    weights = {
        +3: 0.5, +2: 0.5, +1: 1,
        -3: 0.5, -2: 0.5, -1: 0
    }
    wmc = sdd_file_wmc(here / "rsrc" / "test.sdd", weights)
    print("WMC", wmc)
    assert wmc == 0.75, f"{wmc} != 0.75"


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    # test_nnf1()
    test_sdd2()
