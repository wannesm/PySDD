#!/usr/bin/env python3
from pathlib import Path
from pysdd.sdd import SddManager, Vtree


def main():

  # set up vtree and manager
  vtree = Vtree.from_file("input/opt-swap.vtree".encode())
  manager = SddManager.from_vtree(vtree)

  print("reading sdd from file ...")
  alpha = manager.read("input/opt-swap.sdd".encode())
  print(f"  sdd size = {alpha.size()}")

  # ref, perform the minimization, and then de-ref
  alpha.ref()
  print("minimizing sdd size ... ", end="")
  manager.minimize()  # see also manager.minimize_limited()
  print("done!")
  print(f"  sdd size = {alpha.size()}")
  alpha.deref()

  # augment the SDD
  print("augmenting sdd ...")
  beta = alpha * (manager.l(4) + manager.l(5))
  print(f"  sdd size = {beta.size()}")

  # ref, perform the minimization again on new SDD, and then de-ref
  beta.ref()
  print("minimizing sdd ... ", end="")
  manager.minimize()
  print("done!")
  print(f"  sdd size = {beta.size()}")
  beta.deref()


if __name__ == "__main__":
    main()


