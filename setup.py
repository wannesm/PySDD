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
# import numpy
import platform
import os
import sys
import re
from pathlib import Path
from Cython.Build import cythonize

here = Path(os.path.abspath(os.path.dirname(__file__)))

with open('pysdd/__init__.py', 'r') as fd:
    wrapper_version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)
if not wrapper_version:
    raise RuntimeError('Cannot find version information')

sdd_version = "2.0"


libwrapper_path = here / "pysdd" / "lib"
sdd_path = libwrapper_path / f"sdd-{sdd_version}"
lib_path = sdd_path / "lib"
if "Darwin" in platform.platform():
    lib_path = lib_path / "Darwin"
elif "Linux" in platform.platform():
    lib_path = lib_path / "Linux"
inc_path = sdd_path / "include"
src_path = sdd_path / "src"
csrc_path = here / "pysdd" / "src"
c_files_paths = src_path.glob("**/*.c")
c_dirs_paths = set(p.parent for p in src_path.glob("**/*.c"))
all_c_file_paths = [str(p) for p in c_files_paths]# + [str(p) for p in csrc_path.glob("*.c")]
print("Found c files: ", ", ".join([str(p) for p in all_c_file_paths]))

os.environ["LDFLAGS"] = f"-L{lib_path}"
os.environ["CPPFLAGS"] = f"-I{inc_path} " + f"-I{csrc_path} " + \
                         " ".join(f"-I{p}" for p in c_dirs_paths)
# print("-I: " + str(os.environ["CPPFLAGS"]))

ext_modules = cythonize([
    Extension(
        "pysdd.sdd", ["pysdd/sdd.pyx"] + all_c_file_paths,
                    #str(csrc_path / "cli.c")],
                    # os.path.join(src_path, "main.c"),
                    # os.path.join(src_path, "fnf", "compiler-manual.c"),
                    # os.path.join(src_path, "fnf", "compiler-auto.c")],
        extra_objects=[str(lib_path / "libsdd.a")]
        # include_dirs=[numpy.get_include()]
    )],
    gdb_debug=True)

# install_requires = ['numpy', 'cython']
install_requires = ['cython']
tests_require = ['pytest']

with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

setup(
    name='PySDD',
    version=wrapper_version,
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
