#!/usr/bin/env python3
from pathlib import Path
from pysdd.sdd import SddManager, Vtree


here = Path(__file__).parent


def main():

  # set up vtree and manager
  vtree = Vtree.from_file(bytes(here / "input" / "rotate-left.vtree"))
  manager = SddManager.from_vtree(vtree)

  # construct the term X_1 ^ X_2 ^ X_3 ^ X_4
  x = [None] + [manager.literal(i) for i in range(1, 5)]
  alpha = x[1]*x[2]*x[3]*x[4]

  # to perform a rotate, we need the manager's vtree
  manager_vtree = manager.vtree()
  manager_vtree_right = manager_vtree.right()

  print("saving vtree & sdd ...")
  manager_vtree.save_as_dot("output/before-rotate-vtree.dot".encode())
  alpha.save_as_dot("output/before-rotate-sdd.dot".encode())

  # ref alpha (so it is not gc'd)
  alpha.ref()

  # garbage collect (no dead nodes when performing vtree operations)
  print(f"dead sdd nodes = {manager.dead_count()}")
  print("garbage collection ...")
  manager.garbage_collect()
  print(f"dead sdd nodes = {manager.dead_count()}")

  print("left rotating ... ", end="")
  succeeded = manager_vtree_right.rotate_left(manager, 0)
  print("succeeded!" if succeeded == 1 else "did not succeed!")

  # deref alpha, since ref's are no longer needed
  alpha.deref()

  # the root changed after rotation, so get the manager's vtree again
  # this time using root_location
  manager_vtree = manager.vtree()

  print("saving vtree & sdd ...")
  manager_vtree.save_as_dot("output/after-rotate-vtree.dot".encode())
  alpha.save_as_dot("output/after-rotate-sdd.dot".encode())


if __name__ == "__main__":
    main()



