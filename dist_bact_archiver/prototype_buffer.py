# -*- coding: utf-8 -*-
# Author: Andreas Schälicke <andreas.schaelicke@helmholtz-berlin.de>
#          Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date: 2017, 2020
"""Generate the interface code for Google Protobuf

For Google protocol buffer see
https://developers.google.com/protocol-buffers
"""

import os.path
import setuptools

import numpy
from numpy.distutils.misc_util import get_numpy_include_dirs
array_include_dirs = get_numpy_include_dirs()

_log = setuptools.distutils.log

_prefix = os.path.join(os.path.dirname(__file__), os.pardir)
_prefix = os.path.normpath(_prefix)
epics_archiver_backend_path = os.path.join(_prefix, "bact_archiver", "backend")
epics_archiver_backend_path = os.path.abspath(epics_archiver_backend_path)


class GenProtobuf(setuptools.Command):
    """Custom build step for protobuf

    Generate the python and c++ wrapper code from the protocol buffer specifications
    """

    description = "Run protoc to generate python and cpp wrapper files"

    user_options = [
        # The format is (long option, short option, description).
        ('inplace', None, 'create files inplace of proto-file (default)'),
        ('python', None, 'create python wrapper'),
        ('cpp', None, 'create C++ wrapper'),
        ('protoc=', None, 'protoc executable to use')
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.inplace = True
        self.python = False
        self.cpp = False
        self.protoc = None

    def finalize_options(self):
        """Post-process options."""
        if not self.inplace:
            self.announce('inplace False is not support yet',
                          level=_log.WARN)

        if not self.python and not self.cpp:
            self.python = True
            self.cpp = True
            self.announce('select python and C++ wrapper',
                          level=_log.INFO)

    def run(self):
        self.announce("creating Wrapper for Archiver Protocol Buffers",
                      level=_log.INFO)

        t_file = os.path.join(epics_archiver_backend_path, 'EPICSEvent.proto')

        if self.protoc is None:
            protoc = 'protoc'
        else:
            protoc = self.protoc
        #self.announce('using protoc "%s"' %(protoc,), level=_log.INFO)

        args = [protoc, t_file,'--proto_path=%s' %(epics_archiver_backend_path,)]
        if self.cpp:
            self.spawn(args + ['--cpp_out=%s' %(epics_archiver_backend_path,)])
        if self.python:
            self.spawn(args + ['--python_out=%s' %(epics_archiver_backend_path,)])


import bact_archiver_config_features as config_features

cython_extensions = []

c_lib = False
try:
    c_lib = config_features.google_protobuf_c_library
except AttributeError:
    pass
if c_lib:
    # Current assumption: cython is a prerequisite when using c-library for
    # protobuf protocol
    #
    # Could be extended that the c files are distributed, thus distro users do
    # not need to have cython installed
    import sys
    from Cython.Build import cythonize

    libraries=["protobuf"]
    macros=[]
    if sys.platform in ("win32",):
        # That's not all
        # The libprotobuf library has to be in a standard directory or in
        # %PATH%
        libraries=["libprotobuf"]
        macros += [("PROTOBUF_USE_DLLS", 1)]
        pass

    cython_extensions = [
        setuptools.Extension("bact_archiver.backend.EPICSEvent",
                             sources=[
                                 os.path.join(epics_archiver_backend_path, "EPICSEvent.pyx"),
                                 os.path.join(epics_archiver_backend_path, "EPICSEvent.pb.cc"),
                             ],
                             include_dirs = ["."] + array_include_dirs + [epics_archiver_backend_path],
                             define_macros = macros,
                             libraries=libraries,
                             language ="c++"),

        #setuptools.Extension("bact.epics.archiver.backend.example",
        #          [
        #              os.path.join(epics_archiver_backend_path, "example.pyx")
        #              ],
        #          ),
    ]
    cython_extensions = cythonize(cython_extensions)
