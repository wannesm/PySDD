Installation
============

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

