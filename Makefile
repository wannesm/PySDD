
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

.PHONY: build_debug
build_debug: clean
	python3 setup.py --debug build_ext --inplace

.PHONY: prepare_dist
prepare_dist:
	rm -rf dist/*
	python3 setup.py sdist
	@#python3 setup.py sdist bdist_wheel

.PHONY: version
version:
	@python3 -c "import pysdd;print(pysdd.__version__)"

.PHONY: deploy
deploy: prepare_dist
	@echo "Check whether repo is clean"
	git diff-index --quiet HEAD
	@echo "Add tag"
	#git tag "v$$(python3 setup.py --version)"
	versiontag=$$(python3 -c "import pysdd;print(pysdd.__version__)") && git tag "v$$versiontag"
	@echo "Start uploading"
	@echo "-> Use Github actions"
	# twine upload --repository pysdd dist/*

.PHONY: docs
docs:
	export PYTHONPATH=..; cd docs; make html

.PHONY: view-docs
view-docs: docs
	open docs/_build/html/index.html

.PHONY: test
test:
	export PYTHONPATH=.;py.test --ignore=venv --ignore-glob="venv_*"

