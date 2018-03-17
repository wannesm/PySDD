=====
PySDD
=====

Python package to interactively use Sententical Decision Diagrams (SDD).

*This is a beta version, API might change*


------------
Dependencies
------------

* Python >=3.6
* Cython
* SDD package >=2.0: http://reasoning.cs.ucla.edu/sdd/


-----------
Compilation
-----------

Notice: This wrapper requires some small changes to the SDD package.
The changed files are already included in this repository. Do not overwrite
them with the original files.

* Download the package from http://reasoning.cs.ucla.edu/sdd/
* Install the library in this package in directoy ``pysdd/lib/libsdd-2.0``
  without overwriting the already available files
* Run ``python3 setup.py build_ext --inplace`` or ``make build``


--------
Examples
--------

The following example builds an SDD for the formula ``a^b v b^c v c^d``.

.. code-block:: python

    vtree = Vtree(var_count=4, var_order=[2,1,4,3], vtree_type="balanced")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = [manager.literal(i) for i in range(1, 5)]

    # Build SDD for formula
    formula = (a * b) + (b * c) + (c * d)

    # Model Counting
    wmc = formula.wmc(log_mode=False)
    print(f"Model Count: {wmc.propagate()})
    wmc.set_literal_weight(a, 0.5)
    print(f"Weighted Model Count: {wmc.propagate()}")

    # Visualize SDD and Vtree
    with open("output/sdd.dot", "w") as out:
        print(formula.dot(), file=out)
    with open("output/vtree.dot", "w") as out:
        print(vtree.dot(), file=out)

The SDD and Vtree are visualized using Graphviz DOT:

.. image:: https://people.cs.kuleuven.be/wannes.meert/pysdd/sdd.png
.. image:: https://people.cs.kuleuven.be/wannes.meert/pysdd/vtree.png



More examples are available in the ``examples`` and ``docs`` directories.


-----------------
Memory management
-----------------

Python's memory management is not used for the internal datastructures.
Use the SDD library's garbage collection commands (e.g. ref, deref) to
perform memory management.


-------
Contact
-------

* Wannes Meert, KU Leuven, https://people.cs.kuleuven.be/wannes.meert
* Arthur Choi, UCLA, http://web.cs.ucla.edu/~aychoi/


-------
License
-------

Copyright 2018, KU Leuven and Regents of the University of California.

The Python SDD wrapper is licensed under the Apache License, Version 2.0.

