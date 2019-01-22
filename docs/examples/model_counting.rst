Model Counting
==============


Perform Weighted Model Counting on CNF file
-------------------------------------------

.. literalinclude:: ../../examples/wmc-1.py


Perform Weighted Model Counting on CNF file from CLI
----------------------------------------------------

Given a DIMACS file ``test.cnf``

.. literalinclude:: test.cnf


We can run the CLI:

.. code-block:: none

   $ pysdd -c test.cnf
   reading cnf...
   Read CNF: vars=2 clauses=2
   creating initial vtree balanced
   creating manager...
   compiling...

   compilation time         : 0.000 sec
    sdd size                : 2
    sdd node count          : 1
    sdd model count         : 2    0.000 sec
    sdd weighted model count: 0.54    0.000 sec
   done
