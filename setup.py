#!/usr/bin/env python3
"""
__author__ = "Wannes Meert"
__copyright__ = "Copyright 2017 KU Leuven, DTAI Research Group"
__license__ = "APL"

Usage: python3 setup.py build_ext --inplace
"""
from setuptools import setup, Command
from setuptools.extension import Extension
from setuptools.command.test import test as TestCommand
from setuptools.command.sdist import sdist as SDistCommand
from setuptools.command.build_ext import build_ext as BuildExtCommand
import numpy
import platform
import os
import sys
import re
from Cython.Build import cythonize

here = os.path.abspath(os.path.dirname(__file__))

with open('pysdd/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)
if not version:
    raise RuntimeError('Cannot find version information')


sdd_path = os.path.join(here, "pysdd", "lib", "sdd-"+version)
lib_path = os.path.join(sdd_path, "lib")
inc_path = os.path.join(sdd_path, "include")
src_path = os.path.join(sdd_path, "src")
csrc_path = os.path.join(here, "pysdd", "src")

os.environ["LDFLAGS"] = "-L" + lib_path
os.environ["CPPFLAGS"] = "-I" + inc_path + " -I" + csrc_path

ext_modules = cythonize([
    Extension(
        "pysdd.sdd", ["pysdd/sdd.pyx", os.path.join(csrc_path, "cli.c")],
                    # os.path.join(src_path, "main.c"),
                    # os.path.join(src_path, "fnf", "compiler-manual.c"),
                    # os.path.join(src_path, "fnf", "compiler-auto.c")],
        extra_objects=[os.path.join(lib_path, "libsdd.a")],
        include_dirs=[numpy.get_include()]
    )])

install_requires = ['numpy', 'cython']
tests_require = ['pytest']

with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

setup(
    name='PySDD',
    version=version,
    description='Sentential Decision Diagrams',
    long_description=long_description,
    author='Wannes Meert',
    author_email='wannes.meert@cs.kuleuven.be',
    url='https://github.com/wannesm/PySDD',
    packages=["sdd"],
    install_requires=install_requires,
    tests_require=tests_require,
    license='Apache 2.0',
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ),
    keywords='sdd, knowledge compilation',
    ext_modules=ext_modules
)
