"""
compiler_c - SDD

__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

"""

from . cimport sddapi_c

cdef extern from "compiler.h":
    ctypedef struct SddCompilerOptions:
        # input files
        char* cnf_filename         # input cnf filename
        char* dnf_filename         # input dnf filename
        char* vtree_filename       # input vtree filename
        char* sdd_filename         # input sdd filename (.sdd, plain text)
        # output files
        char* output_vtree_filename      # output vtree filename (.vtree, plain text)
        char* output_vtree_dot_filename  # output vtree filename (.dot)
        char* output_sdd_filename        # output sdd filename (.sdd, plain text)
        char* output_sdd_dot_filename    # output sdd filename (.dot)
        # flags
        int minimize_cardinality    # construct sdd that has only minimum cardinality models
        # initial vtree
        char* initial_vtree_type    # initial vtree for manager
        # compilation controls
        int vtree_search_mode       #  vtree search mode
        int post_search             #  post-compilation search
        int verbose                 #  print manager
    ctypedef struct Fnf:
        long long var_count;
        sddapi_c.SddSize litset_count;
    ctypedef Fnf Cnf;
    ctypedef Fnf Dnf;

    sddapi_c.SddNode* fnf_to_sdd(Fnf* fnf, sddapi_c.SddManager* manager);
