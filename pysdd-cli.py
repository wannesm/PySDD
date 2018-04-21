#!/usr/bin/env python3
# encoding: utf-8
"""
pysdd-cli
~~~~~~~~~

PySDD command line interface.

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2018 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import sys

from pysdd import cli

if __name__ == "__main__":
    sys.exit(cli.main())
