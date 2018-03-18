#!/usr/bin/env python3
from pathlib import Path
import math
from pysdd.sdd import SddManager, Vtree, WmcManager


here = Path(__file__).parent


def main():
    # Start from a given CNF and VTREE file
    vtree = Vtree.from_file(bytes(here / "input" / "simple.vtree"))
    sdd = SddManager.from_vtree(vtree)
    print(f"Created an SDD with {sdd.var_count()} variables")
    root = sdd.read_cnf_file(bytes(here / "input" / "simple.cnf"))

    # Model Counting
    wmc = root.wmc(log_mode=True)
    w = wmc.propagate()
    print(f"Model count: {int(math.exp(w))}")

    # Weighted Model Counting
    lits = [None] + [sdd.literal(i) for i in range(1, sdd.var_count() + 1)]
    # Positive literal weight
    wmc.set_literal_weight(lits[1], math.log(0.5))
    # Negative literal weight
    wmc.set_literal_weight(-lits[1], math.log(0.5))
    w = wmc.propagate()
    print(f"Weighted model count: {math.exp(w)}")

    # Visualize SDD and VTREE
    print("saving sdd and vtree ... ", end="")
    with open(here / "output" / "sdd.dot", "w") as out:
        print(sdd.dot(), file=out)
    with open(here / "output" / "vtree.dot", "w") as out:
        print(vtree.dot(), file=out)
    print("done")


if __name__ == "__main__":
    main()

