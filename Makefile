
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

.PHONY: compile-macos-arm
compile-macos-arm:
	export MACOSX_DEPLOYMENT_TARGET=13; cd pysdd/lib/libsdd-2.0; scons -c; scons
	cp pysdd/lib/libsdd-2.0/build/libsdd.* pysdd/lib/sdd-2.0/lib/Darwin-arm
	make clean
	make build

.PHONY: test
test:
	export PYTHONPATH=.;python -m pytest --ignore=venv --ignore-glob="venv_*"

.PHONY: testv
testv:
	export PYTHONPATH=.;python -m pytest -s --ignore=venv --ignore-glob="venv_*"

