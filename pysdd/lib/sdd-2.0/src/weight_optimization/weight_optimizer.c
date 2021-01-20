
#include "weight_optimizer.h"

const long double PI = 3.141592653589793238463;
const long double wo_prior_mean = 0;

long double logProb2Prob(long double logProb) {
	if (logProb > 0 && logProb < 0.0000000000001)
		return 1;
	else
		return expl(logProb);
}

lbfgsfloatval_t _evaluate(void* instance, const lbfgsfloatval_t* cur_weights,
		lbfgsfloatval_t *gradient, const int n, const lbfgsfloatval_t step) {

	struct OptimizationRun* run = (struct OptimizationRun*) instance;

	lbfgsfloatval_t negll = wop_evaluate(run->problem, cur_weights, gradient);

	// in addition to the L1 regularization, add gaussian priors
	lbfgsfloatval_t prior_loss = wo_prior(run->learner, cur_weights, gradient, n);

	return negll + prior_loss;

}

int _progress(void* instance, const lbfgsfloatval_t *x,
		const lbfgsfloatval_t *g, const lbfgsfloatval_t fx,
		const lbfgsfloatval_t xnorm, const lbfgsfloatval_t gnorm,
		const lbfgsfloatval_t step, int n, int k, int ls) {
	return 0;
}

WeightOptimizationProblem wop_new(SddNode* sdd, SddManager* mgr, int m_instances,
	        int n_optimize, int* ind_optimize,  long double* weights_optimize, int* counts_optimize,
	        int n_fix, int* ind_fix,  long double* weights_fix, int* counts_fix ){

    WeightOptimizationProblem wop;

	wop.sdd = sdd;
	wop.mgr = mgr;
	wop.m_instances = m_instances;
	wop.n_optimize = n_optimize;
	wop.ind_optimize = ind_optimize;
	wop.weights_optimize = weights_optimize;
	wop.counts_optimize = counts_optimize;
	wop.loglikelihood = INFINITY;

    // pre-calculate the ll contribution of the fixed features
	long double ll_fix = 0;
	for (int i= 0; i <n_fix; i++) {
	    ll_fix += (counts_fix[i] * weights_fix[i]);
	}
	wop.ll_fix = ll_fix;

    wop.wmcManager = wmc_manager_new(sdd, 1, mgr);

    // set all literal weights to one, so that unused variables are ignored
	for (int i = 1; i <= sdd_manager_var_count(mgr); i++) {
		wmc_set_literal_weight(i, wmc_one_weight(wop.wmcManager), wop.wmcManager);
		wmc_set_literal_weight(-i, wmc_one_weight(wop.wmcManager), wop.wmcManager);
	}

    // set positive literal weights of indicators to be fixed to their fixed weights
	for (int i = 1; i <= n_fix; i++) {
		wmc_set_literal_weight(ind_fix[i], weights_fix[i], wop.wmcManager);
	}

	return wop;
}

void wop_free(WeightOptimizationProblem* wop) {
	if (wop->wmcManager != NULL) {
		wmc_manager_free(wop->wmcManager);
	}
}

SddWmc wop_update_wmc(WeightOptimizationProblem* wop, const lbfgsfloatval_t* cur_weights) {
    // set optimized weights from cur_weights
	for (int i= 0; i <wop->n_optimize; i++) {
	    wmc_set_literal_weight(wop->ind_optimize[i], cur_weights[i], wop->wmcManager);
	}

	// compute WMC
	SddWmc log_wmc = wmc_propagate(wop->wmcManager);
	assert(isfinite(log_wmc));

	return log_wmc;
}

long double wop_infer(WeightOptimizationProblem* wop, const lbfgsfloatval_t* cur_weights, SddWmc log_wmc) {

    // partition function
	long double negll = wop->m_instances * log_wmc;

    // contribution of fixed features to loglikelihood
	negll -= wop->ll_fix;

    // contribution optimized features to loglikelihood
	for (int i= 0; i <wop->n_optimize; i++) {
	    negll -= (wop->counts_optimize[i] * cur_weights[i]);
	}

	assert(negll >= -1e-6);
	return negll;
}

void wop_gradient(WeightOptimizationProblem* wop, lbfgsfloatval_t* gradient) {

	for (int i= 0; i <wop->n_optimize; i++) {
		long double marginalProb = logProb2Prob(
				wmc_literal_pr(wop->ind_optimize[i], wop->wmcManager));
		assert(isfinite(marginalProb));
		assert(marginalProb<=1+1e-6);
		assert(marginalProb>=-1e-6);

		gradient[i] = -(wop->counts_optimize[i] - marginalProb * wop->m_instances);

		assert(isfinite(gradient[i]));
	}
}

// calculate likelihood and gradient of the weights to be optimized
lbfgsfloatval_t wop_evaluate(WeightOptimizationProblem* wop,
        const lbfgsfloatval_t* cur_weights, lbfgsfloatval_t* gradient) {

    SddWmc log_wmc = wop_update_wmc(wop, cur_weights); // this function is necessary for infer and gradient
	long double negll = wop_infer(wop, cur_weights, log_wmc);
	wop_gradient(wop, gradient);

	return negll;
}

/*
When optimization is done: copy last weights and final score to wop
*/
void wop_done(WeightOptimizationProblem* wop, lbfgsfloatval_t *m_x,
		lbfgsfloatval_t fx) {
	for (int i = 0; i < wop->n_optimize; i++) {
		wop->weights_optimize[i] = m_x[i];
	}
	wop->loglikelihood = -fx / wop->m_instances;
}

WeightOptimizer wo_new(long double prior_sigma, long double l1_const, int max_iter,
		long double delta, long double epsilon) {
	WeightOptimizer wo;
	wo.prior_sigma = prior_sigma;
	lbfgs_parameter_init(&wo.settings);
	if (l1_const != 0)
		wo.settings.orthantwise_c = l1_const;
	wo.settings.max_iterations = max_iter;
	wo.settings.delta = delta;
	wo.settings.epsilon = epsilon;

	return wo;
}

int wo_optimize(WeightOptimizer* wo, WeightOptimizationProblem* problem) {

	/* Initialize the variables and settings. */
	lbfgsfloatval_t fx;
	lbfgsfloatval_t *m_x = lbfgs_malloc(problem->n_optimize);
	if (m_x == NULL) {
		printf("ERROR: Failed to allocate a memory block for variables.\n");
		return 1;
	}
	for (int i = 0; i < problem->n_optimize; i++) {
		m_x[i] = problem->weights_optimize[i];
	}
	if (wo->settings.orthantwise_c != 0) {
		wo->settings.linesearch = LBFGS_LINESEARCH_BACKTRACKING; //required by lbfgs lib
		wo->settings.orthantwise_start = 0; //problem->nbUnitFeatures;
		wo->settings.orthantwise_end = problem->n_optimize; // incorporate all parameters for non-unit features in L1 norm
	}

	/*
	 Start the L-BFGS optimization; this will invoke the callback functions
	 evaluate() and progress() when necessary.
	 */
	struct OptimizationRun run;
	run.problem = problem;
	run.learner = wo;
	int ret = lbfgs(problem->n_optimize, m_x, &fx, _evaluate, _progress, &run,
			&wo->settings);

	wop_done(problem, m_x, fx);
	lbfgs_free(m_x);
	return ret;
}

lbfgsfloatval_t wo_prior(WeightOptimizer* wo, const lbfgsfloatval_t* cur_weights,
		lbfgsfloatval_t *gradient, const int n) {

    lbfgsfloatval_t prior = 0;
	if (wo->prior_sigma > 0) {
		for (int i = 0; i < n; i++) {
			prior += (cur_weights[i] - wo_prior_mean)
					* (cur_weights[i] - wo_prior_mean)
					/ (2.0 * wo->prior_sigma * wo->prior_sigma);
			prior += log(wo->prior_sigma) + log(2 * PI) / 2.0;
			gradient[i] -= (wo_prior_mean - cur_weights[i])
					/ (wo->prior_sigma * wo->prior_sigma);

			assert(isfinite(gradient[i]));
		}
		assert(isfinite(negll));
	}
	return prior;
}


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
        long double prior_sigma, long double l1_const, int max_iter, long double delta, long double epsilon) {

	WeightOptimizationProblem wop = wop_new(sdd, mgr, m_instances,
	        n_optimize, ind_optimize,  weights_optimize, counts_optimize,
	        n_fix, ind_fix, weights_fix, counts_fix);

    WeightOptimizer wo = wo_new(prior_sigma, l1_const, max_iter, delta, epsilon);

	wo_optimize(&wo, &wop);
	wop_free(&wop);
}