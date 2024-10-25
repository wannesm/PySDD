#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
setup.py
~~~~~~~~

Usage: python3 setup.py build_ext --inplace

:author: Wannes Meert
:copyright: Copyright 2017-2023 KU Leuven and Regents of the University of California.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext as BuildExtCommand
from setuptools import Distribution
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError
import platform
import os
import re
import shutil
from pathlib import Path


try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

try:
    import cysignals
except ImportError as exc:
    print(f"cysignals not found\n{exc}")
    cysignals = None

print("Python version = " + str(platform.python_version()))


class MyDistribution(Distribution):
    global_options = Distribution.global_options + [
        ('debug', None, 'Compile with debug options on (PySDD option)'),
        ('usecysignals', None, 'Compile with CySignals (PySDD option)')
    ]

    def __init__(self, attrs=None):
        self.debug = 0
        self.usecysignals = 0
        super().__init__(attrs)


# build_type = "debug"
build_type = "optimized"

here = Path(".")  # setup script requires relative paths

with (here / "pysdd" / "__init__.py").open('r') as fd:
    wrapper_version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                                fd.read(), re.MULTILINE).group(1)
if not wrapper_version:
    raise RuntimeError('Cannot find version information')

sdd_version = "2.0"

libwrapper_path = here / "pysdd" / "lib"
sdd_path = libwrapper_path / f"sdd-{sdd_version}"
lib_path = sdd_path / "lib"
inc_path = sdd_path / "include"
src_path = sdd_path / "src"
csrc_path = here / "pysdd" / "src"
# c_files_paths = src_path.glob("**/*.c")
c_files_paths = (src_path / "fnf").glob("*.c")

sdd_extra_inc_path = libwrapper_path / "sdd_extra" / "include"

# weight optimization wrapper
wo_path = libwrapper_path / "weight_optimization"
wo_inc_path = wo_path / "include"
wo_src_path = wo_path / "src"
wo_c_files_paths = wo_src_path.glob("*.c")

c_dirs_paths = set(p.parent for p in src_path.glob("**/*.c")) | {wo_src_path}
all_c_file_paths = [str(p) for p in c_files_paths] + [str(p) for p in wo_c_files_paths]
# print("Found c files: ", ", ".join([str(p) for p in all_c_file_paths]))

#os.environ["LDFLAGS"] = f"-L{lib_path}"
os.environ["CPPFLAGS"] = f"-I{inc_path} " + f"-I{wo_inc_path} " + f"-I{sdd_extra_inc_path} " + f"-I{csrc_path} " + \
                         " ".join(f"-I{p}" for p in c_dirs_paths)
library_dirs = []# [str(lib_path)]
include_dirs = [str(inc_path), str(wo_inc_path), str(sdd_extra_inc_path), str(csrc_path)] + \
               [str(p) for p in c_dirs_paths]

compile_time_env = {'HAVE_CYSIGNALS': False}
# if cysignals is not None:
#     compile_time_env['HAVE_CYSIGNALS'] = True

c_args = {
    'unix': ['-O3', '-Wall'],
    # 'msvc': ['/Ox', '/fp:fast', '/favor:INTEL64', '/Og'],
    'msvc': ['/Ox', '/fp:fast'],
    'mingw32': ['-O3', '-march=native']
}
c_args_debug = {
    'unix': ["-O0", '-g'],
    'msvc': [["-Zi", "/Od"]],
    'mingw32': ["-march=native", "-O0", '-g']
}
l_args = {
    'unix': [],
    'msvc': [],
    'mingw32': ['-static-libgcc', '-static-libstdc++', '-Wl,-Bstatic,--whole-archive',
                '-lwinpthread', '-Wl,--no-whole-archive']
}
l_args_debug = {
    'unix': ['-g'],
    'msvc': ["-debug"],
    'mingw32': ['-g']
}


class MyBuildExtCommand(BuildExtCommand):

    def build_extensions(self):
        global lib_path
        try:
            c = self.compiler.compiler_type
            print("Compiler type: {}".format(c))
            compiler_name = self.compiler.compiler[0]
            print("Compiler name: {}".format(compiler_name))
        except AttributeError as exc:
            output = str(exc)
            if 'MSVCCompiler' in output:
                c = "msvc"
                print("Compiler type: {}".format(c))
                compiler_name = "MSVCCompiler"
                print("Compiler name: {}".format(compiler_name))
            else:
                print("Could not derive compiler type")
                c = "Unknown"
                compiler_name = "Unknown"
        print("--debug: {}".format(self.distribution.debug))
        print("--usecysignals: {}".format(self.distribution.usecysignals))
        # Compiler and linker options
        if self.distribution.debug:
            self.force = True  # force full rebuild in debugging mode
            cur_c_args = c_args_debug
            cur_l_args = l_args_debug
        else:
            cur_c_args = c_args
            cur_l_args = l_args
        if "gcc" in compiler_name:
            cur_c_args["unix"].append("-std=c99")
        if c in cur_c_args:
            args = cur_c_args[c]
            for e in self.extensions:  # type: Extension
                e.extra_compile_args = args
        else:
            print("Unknown compiler type: {}".format(c))
        if c in cur_l_args:
            args = cur_l_args[c]
            for e in self.extensions:  # type: Extension
                e.extra_link_args = args
        if self.distribution.usecysignals:
            if cysignals is not None:
                if self.cython_compile_time_env is None:
                    self.cython_compile_time_env = {'HAVE_CYSIGNALS': True}
                else:
                    self.cython_compile_time_env['HAVE_CYSIGNALS'] = True
            else:
                print("Warning: import cysignals failed")
        # Extra objects
        print('System', platform.system())
        print('platform', platform.platform())
        # lib_path = libwrapper_path / "libsdd-2.0" / "build"
        if "Windows" in platform.system():
            libsdd_path = lib_path / "sdd.lib"
            #shutil.copyfile(lib_path / "sdd.dll", Path(".") / "pysdd")
        else:
            libsdd_path = lib_path / "libsdd.a"
        # if "Darwin" in platform.system():
        #     if "arm" in platform.platform():
        #         cur_lib_path = lib_path / "Darwin-arm"
        #     else:
        #         cur_lib_path = lib_path / "Darwin"
        #     if build_type == "debug":
        #         cur_lib_path = cur_lib_path / "debug"
        #     libsdd_path = cur_lib_path / "libsdd.a"
        # elif "Linux" in platform.system():
        #     if "arm" in platform.platform() or "aarch" in platform.platform():
        #         cur_lib_path = lib_path / "Linux-arm"
        #     else:
        #         cur_lib_path = lib_path / "Linux"
        #     libsdd_path = cur_lib_path / "libsdd.a"
        # elif "Windows" in platform.system():
        #     cur_lib_path = lib_path / "Windows"
        #     libsdd_path = cur_lib_path / "sdd.lib"
        # else:
        #     libsdd_path = lib_path / "libsdd.a"
        for e in self.extensions:  # type: Extension
            e.extra_objects = [str(libsdd_path)]
        BuildExtCommand.build_extensions(self)


if cythonize is not None:
    ext_modules = cythonize([
        Extension(
            "pysdd.sdd", [str(here / "pysdd" / "sdd.pyx")] + all_c_file_paths,
            include_dirs=include_dirs,
            # library_dirs=library_dirs
            # extra_objects=[str(libsdd_path)],
            # extra_compile_args=extra_compile_args,
            # extra_link_args=extra_link_args
            # include_dirs=[numpy.get_include()]
        )],
        compiler_directives={'embedsignature': True},
        # gdb_debug=gdb_debug,
        compile_time_env=compile_time_env)
else:
    ext_modules = []
    print('****************************************')
    print('Cython not yet available, cannot compile')
    print('****************************************')
    raise ImportError('Cython not available')

# install_requires = ['numpy', 'cython']
install_requires = ['cython>=3.0.0']
setup_requires = ['setuptools>=18.0', 'cython>=3.0.0']
tests_require = ['pytest']
dev_require = tests_require + ['cython>=3.0.0']

with (here / 'README.rst').open('r', encoding='utf-8') as f:
    long_description = f.read()

setup_kwargs = {}


def set_setup_kwargs(**kwargs):
    global setup_kwargs
    setup_kwargs = kwargs


set_setup_kwargs(
    name='PySDD',
    version=wrapper_version,
    description='Sentential Decision Diagrams',
    long_description=long_description,
    author='Wannes Meert, Arthur Choi',
    author_email='wannes.meert@cs.kuleuven.be',
    url='https://github.com/wannesm/PySDD',
    project_urls={
        'PySDD documentation': 'https://pysdd.readthedocs.io/en/latest/',
        'PySDD source': 'https://github.com/wannesm/PySDD'
    },
    packages=["pysdd"],
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require={
        'all': ['cysignals', 'numpy'],
        'dev': dev_require
    },
    include_package_data=True,
    package_data={
        '': ['*.pyx', '*.pxd', '*.h', '*.c', '*.so', '*.a', '*.dll', '*.dylib', '*.lib'],
    },
    distclass=MyDistribution,
    cmdclass={
        'build_ext': MyBuildExtCommand
    },
    entry_points={
        'console_scripts': [
            'pysdd = pysdd.cli:main'
        ]},
    python_requires='>=3.6',
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    keywords='sdd, knowledge compilation',
    ext_modules=ext_modules,
    zip_safe=False
)

try:
    setup(**setup_kwargs)
except (CCompilerError, DistutilsExecError, DistutilsPlatformError, IOError, SystemExit) as exc:
    print("********************************************")
    print("ERROR: The C extension could not be compiled")
    print("********************************************")
    print(exc)
    raise exc
