=====
PySDD
=====

Python wrapper package to interactively use `Sentential Decision Diagrams (SDD) <http://reasoning.cs.ucla.edu/sdd/>`_.

Full documentation available on http://pysdd.readthedocs.io.

------------
Installation
------------

.. code-block:: shell

   $ pip install PySDD


--------------
Python package
--------------

The wrapper can be used as a Python package and allows for interactive use.

The following example builds an SDD for the formula ``a∧b ∨ b∧c ∨  c∧d``.

.. code-block:: python

    from pysdd.sdd import SddManager, Vtree, WmcManager
    vtree = Vtree(var_count=4, var_order=[2,1,4,3], vtree_type="balanced")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = sdd.vars

    # Build SDD for formula
    formula = (a & b) | (b & c) | (c & d)

    # Model Counting
    wmc = formula.wmc(log_mode=False)
    print(f"Model Count: {wmc.propagate()}")
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



More examples are available in the ``examples`` directory.
An interactive Jupyter notebook is available in
`notebooks/examples.ipynb <notebooks/examples.ipynb>`_


----------------------
Command Line Interface
----------------------

A Python CLI application is installed if you use pip, ``pysdd``. Or it can be used
directly from the source directory where it is called ``pysdd-cli.py``.
This script mimicks the original sdd binary and adds additional features (e.g. weighted model counting)

.. code-block:: shell

    $ pysdd -h
    $ ./pysdd-cli.py -h
    usage: pysdd-cli.py [-h] [-c FILE | -d FILE | -s FILE] [-v FILE] [-W FILE]
                    [-V FILE] [-R FILE] [-S FILE] [-m] [-t TYPE] [-r K] [-q]
                    [-p] [--log_mode]

    Sentential Decision Diagram, Compiler

    optional arguments:
      -h, --help  show this help message and exit
      -c FILE     set input CNF file
      -d FILE     set input DNF file
      -s FILE     set input SDD file
      -v FILE     set input VTREE file
      -W FILE     set output VTREE file
      -V FILE     set output VTREE (dot) file
      -R FILE     set output SDD file
      -S FILE     set output SDD (dot) file
      -m          minimize the cardinality of compiled sdd
      -t TYPE     set initial vtree type (left/right/vertical/balanced/random)
      -r K        if K>0: invoke vtree search every K clauses. If K=0: disable
                  vtree search. By default (no -r option), dynamic vtree search is
                  enabled
      -q          perform post-compilation vtree search
      -p          verbose output
      --log_mode  weights in log

    Weighted Model Counting is performed if the NNF file containts a line
    formatted as follows: "c weights PW_1 NW_1 ... PW_n NW_n".


-----------------
Memory management
-----------------

Python's memory management is not used for the internal datastructures.
Use the SDD library's garbage collection commands (e.g. ref, deref) to
perform memory management.


-----------------------
Compilation from source
-----------------------

To install from source, make sure to have the correct development tools installed:

* C compiler (see `Installing Cython <https://cython.readthedocs.io/en/latest/src/quickstart/install.html>`_)
* The Python development version that includes Python header files and static library (e.g. libpython3-dev, python-dev, ...)

The build process will download Cython and numpy in an isolated environment.

Then run:

.. code-block:: shell

   $ pip install build
   $ python -m build


To install the main branch:

.. code-block:: shell

   $ pip install git+https://github.com/wannesm/PySDD.git#egg=PySDD



----------
References
----------

This package is inspired by the SDD wrapper used in the probabilistic
programming language `ProbLog <https://dtai.cs.kuleuven.be/problog/>`_.

References:

* Wannes Meert & Arthur Choi, PySDD,
  in `Recent Trends in Knowledge Compilation
  <http://drops.dagstuhl.de/opus/volltexte/2018/8589/pdf/dagrep_v007_i009_p062_17381.pdf>`_,
  Report from Dagstuhl Seminar 17381, Sep 2017.
  Eds. A. Darwiche, P. Marquis, D. Suciu, S. Szeider.

Other languages:

* C: http://reasoning.cs.ucla.edu/sdd/
* Java: https://github.com/jessa/JSDD


-------
Contact
-------

* Wannes Meert, KU Leuven, https://people.cs.kuleuven.be/wannes.meert
* Arthur Choi, UCLA, http://web.cs.ucla.edu/~aychoi/


-------
License
-------

Python SDD wrapper:

Copyright 2017-2024, KU Leuven and Regents of the University of California.
Licensed under the Apache License, Version 2.0.


SDD package:

Copyright 2013-2018, Regents of the University of California
Licensed under the Apache License, Version 2.0.
