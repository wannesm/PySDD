"""
io
__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

"""

cimport sddapi_c
cimport compiler_c

# cdef extern from "io.c":
#     char* read_file(const char* filename)
#     char* filter_comments(const char* buffer)
#

cdef extern from "io_wrapper.h":
    compiler_c.Fnf* read_fnf_wrapper(const char* filename)
    compiler_c.Cnf* read_cnf_wrapper(const char* filename)
    compiler_c.Dnf* read_dnf_wrapper(const char* filename)
