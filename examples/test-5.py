#!/usr/bin/env python3
from pathlib import Path
from pysdd.sdd import SddManager, Vtree


here = Path(__file__).parent


def main():

  # set up vtree and manager
  vtree = Vtree.from_file(bytes(here / "input" / "big-swap.vtree"))
  manager = SddManager.from_vtree(vtree)

  print("reading sdd from file ...")
  alpha = manager.read_sdd_file("input/big-swap.sdd".encode())
  print(f"  sdd size = {alpha.size()}")

  # to perform a swap, we need the manager's vtree
  manager_vtree = manager.vtree()

  # ref alpha (no dead nodes when swapping)
  alpha.ref()

  # using size of sdd normalized for manager_vtree as baseline for limit
  manager.init_vtree_size_limit(manager_vtree)

  limit = 2.0
  manager.set_vtree_operation_size_limit(limit)

  print(f"modifying vtree (swap node 7) (limit growth by {limit:.1f}x) ... ", end="")
  succeeded = manager_vtree.swap(manager, 1)  # limited
  print("succeeded!" if succeeded == 1 else "did not succeed!")
  print(f"  sdd size = {alpha.size()}")

  print("modifying vtree (swap node 7) (no limit) ... ", end="")
  succeeded = manager_vtree.swap(manager, 0)  # not limited
  print("succeeded!" if succeeded == 1 else "did not succeed!")
  print(f"  sdd size = {alpha.size()}")

  print("updating baseline of size limit ...")
  manager.update_vtree_size_limit()

  left_vtree = manager_vtree.left()
  limit = 1.2
  manager.set_vtree_operation_size_limit(limit)
  print(f"modifying vtree (swap node 5) (limit growth by {limit}x) ... ", end="")
  succeeded = left_vtree.swap(manager, 1)  # limited
  print("succeeded!" if succeeded == 1 else "did not succeed!")
  print(f"  sdd size = {alpha.size()}")

  limit = 1.3
  manager.set_vtree_operation_size_limit(limit)
  print(f"modifying vtree (swap node 5) (limit growth by {limit}x) ... ", end="")
  succeeded = left_vtree.swap(manager, 1)  # limited
  print("succeeded!" if succeeded == 1 else "did not succeed!")
  print(f"  sdd size = {alpha.size()}")

  # deref alpha, since ref's are no longer needed
  alpha.deref()

if __name__ == "__main__":
    main()



