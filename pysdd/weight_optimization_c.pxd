# -*- coding: UTF-8 -*-
"""
pysdd.weight_optimization_c
~~~~~~~~~~~

:author: Jessa Bekker
:copyright: Copyright 2017-2018 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
cimport sddapi_c

cdef extern from "weight_optimizer.h":

    void optimize_weights(sddapi_c.SddNode* sdd, sddapi_c.SddManager* mgr, int m_instances,
                          int n_optimize, int* ind_optimize, double* weights_optimize, int* counts_optimize,
                          int n_fix, int* ind_fix, double* weights_fix,
                          long double prior_sigma, long double l1_const, int max_iter, long double delta,
                          long double epsilon)