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

* Download the SDD package from http://reasoning.cs.ucla.edu/sdd/.
* Install the SDD package in the PySDD package in directories
  ``pysdd/lib/sdd-2.0`` and ``pysdd/lib/sddlib-2.0`` without overwriting
  the already available files.
* Run ``python3 setup.py build_ext --inplace`` or ``make build`` to compile the
  library in the current directory. If you want to install the library such
  that the library is available for your local installation or in your virtual
  environment, use ``python3 setup.py install``.

For some Linux platforms, it might be necessary to recompile the libsdd-2.0 code with
the gcc option ``-fPIC`` and replace the ``pysdd/lib/sdd-2.0/lib/Linux/libsdd.a``
library with your newly compiled version.
