
LIB=sdd

.PHONY: clean
clean:
	python3 setup.py clean
	rm -f ${LIB}/sdd*.c
	rm -f ${LIB}/sdd*.so

.PHONY: build
build:
	python3 setup.py build_ext --inplace
