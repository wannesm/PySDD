# -*- coding: UTF-8 -*-
"""
pysdd.fnf_c
~~~~~~~~~~~

:author: Wannes Meert, Arthur Choi
:copyright: Copyright 2017-2018 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
from . cimport sddapi_c
from . cimport compiler_c

cdef extern from "fnf.h":
    void free_fnf(compiler_c.Fnf* fnf)

# cdef extern from "fnf_wrapper.h":
#     void free_fnf_wrapper(compiler_c.Fnf* fnf)
