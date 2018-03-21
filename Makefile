
LIB=pysdd

.PHONY: clean
clean:
	python3 setup.py clean
	rm -f ${LIB}/sdd*.c
	rm -f ${LIB}/sdd*.so
	rm -fr build/*

.PHONY: build
build:
	python3 setup.py build_ext --inplace

.PHONY: docs
docs:
	cd docs; make html

.PHONY: view-docs
view-docs: docs
	open docs/_build/html/index.html

