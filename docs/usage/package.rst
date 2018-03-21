
Python package
==============

The wrapper can be used as a Python package and allows for interactive use.

The following example builds an SDD for the formula ``a∧b ∨ b∧c ∨  c∧d``.

.. code-block:: python

    from pysdd.sdd import SddManager, Vtree, WmcManager
    vtree = Vtree(var_count=4, var_order=[2,1,4,3], vtree_type="balanced")
    sdd = SddManager.from_vtree(vtree)
    a, b, c, d = [manager.literal(i) for i in range(1, 5)]

    # Build SDD for formula
    formula = (a & b) | (b & c) | (c & d)

    # Model Counting
    wmc = formula.wmc(log_mode=False)
    print(f"Model Count: {wmc.propagate()}")
    wmc.set_literal_weight(a, 0.5)
    print(f"Weighted Model Count: {wmc.propagate()}")

    # Visualize SDD and Vtree
    with open("output/sdd.dot", "w") as out:
        print(formula.dot(), file=out)
    with open("output/vtree.dot", "w") as out:
        print(vtree.dot(), file=out)

The SDD and Vtree are visualized using Graphviz DOT:

.. image:: https://people.cs.kuleuven.be/wannes.meert/pysdd/sdd.png
.. image:: https://people.cs.kuleuven.be/wannes.meert/pysdd/vtree.png



More examples are available in the ``examples`` directory.
An interactive Jupyter notebook is available in
`docs/examples.ipynb <docs/examples.ipynb>`_

