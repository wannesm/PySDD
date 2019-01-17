Conditioning
============

There are three ways to compute the weighted model count given that you observe the value of one or more literals:

* Using the condition command
* Using a conjunction
* Using the weights

We will use the following example, a formula representing the disjunction of ``a`` and ``b``:

.. code-block:: python

    mgr = SddManager(var_count=2)
    a, b = mgr.vars
    f = a | b
    f.wmc(log_mode=False).propagate()


Using the condition command
---------------------------

If we want to know the WMC given that ``a`` is true, we can condition the SDD on ``a``:

.. code-block:: python

    f_a = f.condition(a)


Now, ``f_a`` will represent the formula ``true``. This is an efficient method to alter the sdd.

Note that conditioning is defined as an operation on the circuit, not the WMC. This is why the new SDD is simply
``true``. This also means that the WMC on this new SDD will be 4 instead of 2 as you would expect. To get the
correct model count, you have to ignore the possible values for ``a`` and thus use 4/2=2.


Using a conjunction
-------------------

We can also conjoin the formula with the positive literal ``a``:

.. code-block:: python

    f_a = f & a


Now, ``f_a`` will represent the formula ``a``. This method is more expensive since it optimizes a formula instead of
replacing a literal.


Using the weights
-----------------

If you need to condition on multiple possible value assignments, it is not useful to create a new SDD for every
assignment. In this case, you can alter the weights for WMC and iterate over all required value assignments:

.. code-block:: python

    wmc = f.wmc(log_mode=False)
    wmc.set_literal_weight(a, 1)   # Set the required value for literal a to 1
    wmc.set_literal_weight(-a, 0)  # Set the complement to 0
    wmc.propagate()


For literal ``a`` the three options are weight(a,-a)=(1,1) for no conditioning, weight(a,-a)=(1,0) for ``a`` is true,
and weight(a,-a)=(0,1) for ``a`` is false.

