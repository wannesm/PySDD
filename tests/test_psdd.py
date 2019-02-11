from pysdd.util import psdd_file_wmc
import sys
import os
import math
import logging
from pathlib import Path
import tempfile


logger = logging.getLogger("pysdd")
here = Path(__file__).parent
directory = Path(tempfile.gettempdir())
counter = 0


def test_psdd1():
    wmc = psdd_file_wmc(here / "rsrc" / "loop.psdd")
    wmc = math.exp(wmc)
    assert wmc == 1.0, f"1.0 != {wmc}"


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(".")))
    print(f"Saving files to {directory}")
    test_psdd1()
