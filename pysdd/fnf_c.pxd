"""
fnf
__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

"""

cimport sddapi_c
cimport compiler_c

cdef extern from "fnf.h":
    void free_fnf(compiler_c.Fnf* fnf)

# cdef extern from "fnf_wrapper.h":
#     void free_fnf_wrapper(compiler_c.Fnf* fnf)
