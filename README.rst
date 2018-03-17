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
* SDD package <http://reasoning.cs.ucla.edu/sdd/>


-----------
Compilation
-----------

Notice: This wrapper requires some small changes to the SDD package.
The changed files are already included in this repository. Do not overwrite
them with the original files.

* Download the package from <http://reasoning.cs.ucla.edu/sdd/>
* Install the library as `pysdd/lib/libsdd-2.0` without overwriting the
  already available files
* Run `python3 setup.py build_ext --inplace` or `make build`


-----------------
Memory management
-----------------

Automatic memory management is not implemented. Use the SDD library's ref and deref commands.


-------
Contact
-------

* Wannes Meert, KU Leuven
* Arthur Choi, UCLA


-------
License
-------

Copyright 2018, KU Leuven
Copyright 2018, Regents of the University of California

The Python wrapper is Licensed under the Apache License, Version 2.0.

