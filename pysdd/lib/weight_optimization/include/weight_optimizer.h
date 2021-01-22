#ifndef WEIGHT_OPTIMIZERC_H_
#define WEIGHT_OPTIMIZERC_H_
#include <stdio.h>
#include <math.h>
#include "lbfgs.h"
#include <sddapi.h>
#include <assert.h>

typedef struct WeightOptimizationProblem WeightOptimizationProblem;
struct WeightOptimizationProblem {
	SddNode* sdd;
	SddManager* mgr;
	int nb_instances;
	int n; // num_features to optimize
	int* lits;
	double* weights;
	int* counts;
	WmcManager* wmcManager;
	long double loglikelihood;
};

typedef struct WeightOptimizer WeightOptimizer;
struct WeightOptimizer {
	long double prior_sigma;
	lbfgs_parameter_t settings;
};

struct OptimizationRun {
	WeightOptimizationProblem* problem;
	WeightOptimizer* learner;
};

extern const long double PI;
extern const long double wo_prior_mean;

long double logProb2Prob(long double logProb);

lbfgsfloatval_t _evaluate(void* instance,
		const lbfgsfloatval_t* cur_weights, lbfgsfloatval_t *gradient,
		const int n, const lbfgsfloatval_t step);

int _progress(void* instance, const lbfgsfloatval_t *x,
		const lbfgsfloatval_t *g, const lbfgsfloatval_t fx,
		const lbfgsfloatval_t xnorm, const lbfgsfloatval_t gnorm,
		const lbfgsfloatval_t step, int n, int k, int ls);

// constructor weightOptimization
WeightOptimizationProblem wop_new(SddNode* sdd, SddManager* mgr, int m_instances,
	        int n_optimize, int* lits_optimize,  double* weights_optimize, int* counts_optimize,
	        int n_fix, int* lits_fix,  double* weights_fix);

void wop_free(WeightOptimizationProblem* wop);


// weight update functions
SddWmc wop_update_wmc(WeightOptimizationProblem* wop, const lbfgsfloatval_t* cur_weights);
long double wop_infer(WeightOptimizationProblem* wop, const lbfgsfloatval_t* cur_weights, SddWmc log_wmc);
void wop_gradient(WeightOptimizationProblem* wop, lbfgsfloatval_t* gradient);
lbfgsfloatval_t wop_evaluate(WeightOptimizationProblem* wop,
		const lbfgsfloatval_t* cur_weights, lbfgsfloatval_t* gradient);
void wop_done(WeightOptimizationProblem* wop, lbfgsfloatval_t *m_x,
		lbfgsfloatval_t fx);

WeightOptimizer wo_new(long double prior_sigma, long double l1_const, int max_iter,
		long double delta, long double epsilon);
int wo_optimize(WeightOptimizer* wo, WeightOptimizationProblem* problem);

lbfgsfloatval_t wo_prior(WeightOptimizer* wo, const lbfgsfloatval_t* cur_weights,
		lbfgsfloatval_t *gradient, const int n);


/*
    Optimize the SDD literal log weights to maximize the log likelihood of the weights for some data
    using l-BFGS optimization.
    I.e. optimize the probabilistic model encoded by the SDD: https://doi.org/10.1016/j.artint.2007.11.002

    The data is characterized by the number of instances (m) and the counts of instances in which the literals of the
    to-be-optimized weights are true.

    Not all literal weights need to be optimized.
    The weights of the literals that are not optimized are by default set to log(1)=0, so that they do not affect the LL.
    Alternatively, fixed weights can be provided for literals through lits_fix and weights_fix.


    preconditions:
     - 1 <= abs(lit)) <= sdd_manager_var_count(mgr) for lit in lits_optimize and lits_fix
     - lits_optimize & lits_fix = {}  (intersection of lits_optimize and lits_fix is empty)

    params:
    - *SddNode sdd: SDD
    - *SddManager mgr: SDD manager
    - int m_instances: The number of instances in the data
    - int n_optimize: The number of weights to be optimized
    - int[n_optimize] lits_optimize: The literals whose weights are to be optimized.
    - int[n_optimize] counts_optimize: counts_optimize[i] is the count of instances in which literal lits_optimize[i] is true.
    - double[n_optimize] weights_optimize: weights_optimize[i] is the initial weight for literal lits_optimize[i]
    - int n_fix: The number of weights to be fixed (to other values than log(1)=0)
    - int[n_fix] lits_fix: The literals whose weights are to be fixed
    - double[n_fix] weights_fix: weights_fix[i] is the fixed weight for literal lits_fix[i]
    - long double prior_sigma: sigma of gaussian prior on weights
    - long double l1_const: strength of l1 regularisation
    - int max_iter: maximum number of l-bfgs iterations
    - long double delta: delta for convergence test in l-bfgs, it determines the minimum rate of decrease of the objective function
    - long double epsilon: distance for delta-based convergence test in l-bfgs

    result: The weights in weight_optimize are now optimized
*/
void optimize_weights(SddNode* sdd, SddManager* mgr, int m_instances,
        int n_optimize, int* lits_optimize,  double* weights_optimize, int* counts_optimize,
        int n_fix, int* lits_fix,  double* weights_fix,
        long double prior_sigma, long double l1_const, int max_iter, long double delta, long double epsilon);


#endif /* WEIGHTLEARNERC_H_ */
