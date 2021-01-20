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
	int m_instances;
	int n_optimize; // num_features to optimize
	int* ind_optimize;
	long double* weights_optimize;
	int* counts_optimize;
	long double ll_fix;
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
	        int n_optimize, int* ind_optimize,  long double* weights_optimize, int* counts_optimize,
	        int n_fix, int* ind_fix,  long double* weights_fix, int* counts_fix);

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
    n, ind, weights and counts input parameters come for optimize and fix.
     - optimize refers to the weights to be optimized
     - fix refers to the weights that should be used when evaluating the model, but are to remain fixed

    n: number of weights
    ind: array of length n with the indicators that the weights/counts refer to
    weights: feature weights in model. weights[i] is the weight of feature ind[i]
    counts: feature counts in data. counts[i] is the count of feature ind[i]

    max(n)<= sdd_manager_var_count(mgr)

    indicators that are not in ind_fix nor ind_optimize are not used, i.e. both their literal weights are set to 0.
*/
void optimize_weights(SddNode* sdd, SddManager* mgr, int m_instances,
        int n_optimize, int* ind_optimize,  long double* weights_optimize, int* counts_optimize,
        int n_fix, int* ind_fix,  long double* weights_fix, int* counts_fix,
        long double prior_sigma, long double l1_const, int max_iter, long double delta, long double epsilon);


#endif /* WEIGHTLEARNERC_H_ */
