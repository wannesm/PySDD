"""
io
__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

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
