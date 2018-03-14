"""
compiler_c - SDD

__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

"""

cimport sddapi_c

cdef extern from "compiler.h":
    ctypedef struct SddCompilerOptions:
        pass
    ctypedef struct Fnf:
        long var_count;
        sddapi_c.SddSize litset_count;
    ctypedef Fnf Cnf;
    ctypedef Fnf Dnf;

    sddapi_c.SddNode* fnf_to_sdd_auto(Fnf* fnf, sddapi_c.SddManager* manager)
    sddapi_c.SddNode* fnf_to_sdd_manual(Fnf* fnf, sddapi_c.SddManager* manager)
    sddapi_c.SddNode* fnf_to_sdd(Fnf* fnf, sddapi_c.SddManager* manager);
