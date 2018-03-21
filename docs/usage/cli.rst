
Command Line Interface
======================

A Python CLI application is included, ``pysdd-cli.py``, that mimicks the
original sdd binary.

.. code-block:: shell

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

