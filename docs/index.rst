.. PySDD documentation master file, created by
   sphinx-quickstart on Wed Mar 21 16:36:46 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PySDD documentation
===================

Python package for Sentential Decision Diagrams (SDD).
Source available on https://github.com/wannesm/PySDD.

The SDD can be thought of as a "data structure" for representing Boolean functions,
since SDDs are canonical and support a number of efficient operations for constructing
and manipulating Boolean functions.

The open-source C SDD package allows users to construct, manipulate and optimize SDDs and
is developed by Arthur Choi and Adnan Darwiche at
`UCLA's Automated Reasoning Group <http://reasoning.cs.ucla.edu>`_.
This Python wrapper is a collaboration between UCLA's Automated Reasoning Group and
`KU Leuven's Artificial Intelligence research group (DTAI) <https://dtai.cs.kuleuven.be>`_.

.. toctree::
   :caption: Usage
   :maxdepth: 2

   usage/installation
   usage/package
   usage/cli
   usage/references
   usage/contact



.. toctree::
   :caption: Examples

   examples/build_formula.rst
   examples/model_counting.rst
   git examples/cli_examples.rst



.. toctree::
   :caption: Classes

   classes/SddManager
   classes/SddNode
   classes/Fnf
   classes/Vtree
   classes/WmcManager


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
