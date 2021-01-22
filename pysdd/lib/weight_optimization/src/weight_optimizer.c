
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
	        int n_optimize, int* lits_optimize,  double* weights_optimize, int* counts_optimize,
	        int n_fix, int* lits_fix,  double* weights_fix){

    WeightOptimizationProblem wop;

	wop.sdd = sdd;
	wop.mgr = mgr;
	wop.nb_instances = m_instances;
	wop.n = n_optimize;
	wop.lits = lits_optimize;
	wop.weights = weights_optimize;
	wop.counts = counts_optimize;

    // Initialize weighted model counter in log mode.
    // The neutral weight in log mode is log(1)=0
    wop.wmcManager = wmc_manager_new(sdd, 1, mgr);

    // set all literal weights to the neutral weight log(1)=0
    // Literals that are not set later (by fixing them or optimizing them) will thus have this weight,
    // meaning that these literal weights doe not affect the LL
	for (int i = 1; i <= sdd_manager_var_count(mgr); i++) {
		wmc_set_literal_weight(i, wmc_one_weight(wop.wmcManager), wop.wmcManager);
		wmc_set_literal_weight(-i, wmc_one_weight(wop.wmcManager), wop.wmcManager);
	}

    // set literal weights of indicators to be fixed to their fixed weights
	for (int i = 1; i <= n_fix; i++) {
		wmc_set_literal_weight(lits_fix[i], weights_fix[i], wop.wmcManager);
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
	for (int i= 0; i <wop->n; i++) {
	    wmc_set_literal_weight(wop->lits[i], cur_weights[i], wop->wmcManager);
	}

	// compute partition function as the weighted model count
	SddWmc log_wmc = wmc_propagate(wop->wmcManager);
	assert(isfinite(log_wmc));

	return log_wmc;
}

/*
Infer the negative log likelihood of the model, given the example counts

Derivation of log likelihood calculation:

    weight(example) = product_k weight_k ^ literal_k_active_in_example
    log(weight(example) = sum_k log(weight_k) * literal_k_active_in_example

    Pr(example) = weight(example)/Z
    Z = partition function = sum_world weight(world)  (sum of the weights of all possible worlds)

    log( Pr(example)) = sum_k log(weight_k) * literal_k_active_in_example - log(Z)

    log LL = sum_examples log( Pr(example))
       = sum_examples sum_k log(weight_k) * literal_k_active_in_example - log(Z)
       = sum_k log(weight_k) * count_examples(literal_k_active_in_example) - log(Z)*nb_instances

    -log LL = log(Z)*nb_instances - sum_k log(weight_k) * count_examples(literal_k_active_in_example)

    Literals with log(weight)=log(1)=0 do not contribute to the LL, so they can be ignored in the calculation

In the implementation, the contribution of the literals with fixed weights is not added to the log likelihood.
   ( sum_k_fixed log(weight_k_fixed) * count_examples(literal_k_fixed_active_in_example) )
Therefore, when fixed weights are used, the log likelihood is incorrect, but with a  constant difference.
Minimizing this number is equivalent to minimizing the correct log likelihood
*/
long double wop_infer(WeightOptimizationProblem* wop, const lbfgsfloatval_t* cur_weights, SddWmc log_wmc) {

    // log partition function
	long double negll = wop->nb_instances * log_wmc;

    // contribution optimized features to loglikelihood
	for (int i= 0; i <wop->n; i++) {
	    negll -= (wop->counts[i] * cur_weights[i]);
	}

	assert(negll >= -1e-6);
	return negll;
}

/*
The gradient is the negative difference between the literal probability in the model and the data.
https://dl.acm.org/doi/10.5555/2283516.2283536
*/
void wop_gradient(WeightOptimizationProblem* wop, lbfgsfloatval_t* gradient) {

	for (int i= 0; i <wop->n; i++) {
		long double marginalProb = logProb2Prob(
				wmc_literal_pr(wop->lits[i], wop->wmcManager));
		assert(isfinite(marginalProb));
		assert(marginalProb<=1+1e-6);
		assert(marginalProb>=-1e-6);

		gradient[i] = -(wop->counts[i] - marginalProb * wop->nb_instances);

		assert(isfinite(gradient[i]));
	}
}

/*
calculate likelihood and gradient of the weights to be optimized
*/
lbfgsfloatval_t wop_evaluate(WeightOptimizationProblem* wop,
        const lbfgsfloatval_t* cur_weights, lbfgsfloatval_t* gradient) {

    SddWmc log_wmc = wop_update_wmc(wop, cur_weights); // this function is necessary for infer and gradient
	long double negll = wop_infer(wop, cur_weights, log_wmc);
	wop_gradient(wop, gradient);

	return negll;
}

/*
When optimization is done: copy optimized weights to wop
*/
void wop_done(WeightOptimizationProblem* wop, lbfgsfloatval_t *m_x,
		lbfgsfloatval_t fx) {
	for (int i = 0; i < wop->n; i++) {
		wop->weights[i] = (double) m_x[i];
	}
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
	lbfgsfloatval_t *m_x = lbfgs_malloc(problem->n);
	if (m_x == NULL) {
		printf("ERROR: Failed to allocate a memory block for variables.\n");
		return 1;
	}
	for (int i = 0; i < problem->n; i++) {
		m_x[i] = (lbfgsfloatval_t) problem->weights[i];
	}
	if (wo->settings.orthantwise_c != 0) {
		wo->settings.linesearch = LBFGS_LINESEARCH_BACKTRACKING; //required by lbfgs lib
		wo->settings.orthantwise_start = 0; //problem->nbUnitFeatures;
		wo->settings.orthantwise_end = problem->n; // incorporate all parameters for non-unit features in L1 norm
	}

	/*
	 Start the L-BFGS optimization; this will invoke the callback functions
	 evaluate() and progress() when necessary.
	 */
	struct OptimizationRun run;
	run.problem = problem;
	run.learner = wo;
	int ret = lbfgs(problem->n, m_x, &fx, _evaluate, _progress, &run,
			&wo->settings);

	wop_done(problem, m_x, fx);
	lbfgs_free(m_x);
	return ret;
}

/*
Calculate the gaussian prior on the weights and add it to the gradient
*/
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
Doc in weight_optimizer.h
*/
void optimize_weights(SddNode* sdd, SddManager* mgr, int m_instances,
        int n_optimize, int* lits_optimize,  double* weights_optimize, int* counts_optimize,
        int n_fix, int* lits_fix,  double* weights_fix,
        long double prior_sigma, long double l1_const, int max_iter, long double delta, long double epsilon) {

	WeightOptimizationProblem wop = wop_new(sdd, mgr, m_instances,
	        n_optimize, lits_optimize,  weights_optimize, counts_optimize,
	        n_fix, lits_fix, weights_fix);

    WeightOptimizer wo = wo_new(prior_sigma, l1_const, max_iter, delta, epsilon);

	wo_optimize(&wo, &wop);
	wop_free(&wop);
}