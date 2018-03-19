#!/usr/bin/env python3
from pathlib import Path
from pysdd.sdd import SddManager, Vtree


def main():

  # set up vtree and manager
  var_count = 4
  vtree_type = "right".encode()
  vtree = Vtree(var_count=var_count, vtree_type=vtree_type)
  manager = SddManager(vtree=vtree)

  x = [None] + [manager.literal(i) for i in range(1,5)]

  # construct the term X_1 ^ X_2 ^ X_3 ^ X_4
  alpha =  x[1] &  x[2] & x[3] & x[4]

  # construct the term ~X_1 ^ X_2 ^ X_3 ^ X_4
  beta  = ~x[1] &  x[2] & x[3] & x[4]

  # construct the term ~X_1 ^ ~X_2 ^ X_3 ^ X_4
  gamma = ~x[1] & ~x[2] & x[3] & x[4]

  print("== before referencing:")
  print(f"  live sdd size = {manager.live_size()}")
  print(f"  dead sdd size = {manager.dead_size()}")

  # ref SDDs so that they are not garbage collected
  alpha.ref()
  beta.ref()
  gamma.ref()
  print("== after referencing:")
  print(f"  live sdd size = {manager.live_size()}")
  print(f"  dead sdd size = {manager.dead_size()}")

  # garbage collect
  manager.garbage_collect()
  print("== after garbage collection:");
  print(f"  live sdd size = {manager.live_size()}")
  print(f"  dead sdd size = {manager.dead_size()}")

  alpha.deref()
  beta.deref()
  gamma.deref()

  print("saving vtree & shared sdd ...")
  if not Path("output").is_dir():
      raise Exception(f"Directory 'output' does not exist")
  vtree.save_as_dot("output/shared-vtree.dot".encode())
  manager.shared_save_as_dot("output/shared.dot".encode())


if __name__ == "__main__":
    main()

