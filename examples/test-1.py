#!/usr/bin/env python3
from pysdd.sdd import SddManager, Vtree


def main():
    # set up vtree and manager
    var_count = 4
    var_order = [2,1,4,3]
    vtree_type = "balanced"

    vtree = Vtree(var_count, var_order, vtree_type)
    manager = SddManager.from_vtree(vtree)

    # construct a formula (A^B)v(B^C)v(C^D)
    print("constructing SDD ... ")
    a, b, c, d = [manager.literal(i) for i in range(1, 5)]
    alpha = (a & b) | (b & c) | (c & d)
    print("done")

    print("saving sdd and vtree ... ")
    with open("output/sdd.dot", "w") as out:
        print(alpha.dot(), file=out)
    with open("output/vtree.dot", "w") as out:
        print(vtree.dot(), file=out)
    print("done")


if __name__ == "__main__":
    main()

