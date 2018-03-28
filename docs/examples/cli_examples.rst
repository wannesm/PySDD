Command Line: pysdd-cli.py
==========================


Weighted Model Counting on CNF file
-----------------------------------

Given a DIMACS formatted CNF, ``examples/input/simple.cnf``:

.. literalinclude:: ../../examples/input/simple.cnf


You can use the ``pysdd-cli.py`` program to perform SDD compilation and 
weighted model counting:

.. code-block:: none

    $ ./pysdd-cli.py -c examples/input/simple.cnf -W output.vtree -R output.sdd
    reading cnf...
    Read CNF: vars=6 clauses=3
    creating initial vtree balanced
    creating manager...
    compiling...
    
    compilation time         : 0.001 sec
     sdd size                : 9
     sdd node count          : 4
     sdd model count         : 36    0.000 sec
     sdd weighted model count: 0.5625    0.000 sec
    saving compiled sdd ...done
    saving vtree ...done
    done

The resulting SDD is:

.. code-block:: none

    c ids of sdd nodes start at 0
    c sdd nodes appear bottom-up, children before parents
    c
    c file syntax:
    c sdd count-of-sdd-nodes
    c F id-of-false-sdd-node
    c T id-of-true-sdd-node
    c L id-of-literal-sdd-node id-of-vtree literal
    c D id-of-decomposition-sdd-node id-of-vtree number-of-elements {id-of-prime id-of-sub}*
    c
    sdd 15
    L 1 0 1
    L 4 4 2
    L 5 6 -3
    L 6 4 -2
    F 7
    D 3 5 2 4 5 6 7
    L 8 10 6
    L 9 8 5
    L 11 6 3
    D 10 5 2 4 11 6 7
    T 12
    D 2 7 3 3 8 6 9 10 12
    L 13 0 -1
    L 14 2 4
    D 0 1 2 1 2 13 14


And the resulting vtree is:

.. code-block:: none

    c ids of vtree nodes start at 0
    c ids of variables start at 1
    c vtree nodes appear bottom-up, children before parents
    c
    c file syntax:
    c vtree number-of-nodes-in-vtree
    c L id-of-leaf-vtree-node id-of-variable
    c I id-of-internal-vtree-node id-of-left-child id-of-right-child
    c
    vtree 11
    L 0 1
    L 2 4
    L 4 2
    L 6 3
    I 5 4 6
    I 3 2 5
    L 8 5
    L 10 6
    I 9 8 10
    I 7 3 9
    I 1 0 7 


