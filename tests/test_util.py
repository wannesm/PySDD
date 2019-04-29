from pysdd.util import BitArray
import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger("pysdd")


def test_bitarray1():
    b = BitArray(10)
    print(b)
    assert b[4] is False
    assert b[3] is False
    assert b[2] is False
    b[4] = 1
    b[2] = True
    print(b)
    assert b[4] is True
    assert b[3] is False
    assert b[2] is True
    b[4] = 0
    b[2] = False
    print(b)
    assert b[4] is False
    assert b[3] is False
    assert b[2] is False


def test_bitarray2():
    b = BitArray(100)  # more than 32 bits
    print(b)
    assert b[60] is False
    assert b[90] is False
    b[60] = True
    b[90] = True
    print(b)
    assert b[60] is True
    assert b[90] is True


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    directory = Path(os.environ.get('TESTDIR', Path(__file__).parent))
    print(f"Saving files to {directory}")
    test_bitarray1()
