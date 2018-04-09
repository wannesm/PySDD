# -*- coding: UTF-8 -*-
"""
pysdd.io_c
~~~~~~~~~~

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2018 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
cimport sddapi_c
cimport compiler_c

cdef extern from "io.h":
    compiler_c.Fnf* read_fnf(const char* filename);
    compiler_c.Cnf* read_cnf(const char* filename);
    compiler_c.Dnf* read_dnf(const char* filename);


# cdef extern from "io_wrapper.h":
#     compiler_c.Fnf* read_fnf_wrapper(const char* filename)
#     compiler_c.Cnf* read_cnf_wrapper(const char* filename)
#     compiler_c.Dnf* read_dnf_wrapper(const char* filename)
