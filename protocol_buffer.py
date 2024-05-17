# -*- coding: utf-8 -*-
# Author: Andreas Schälicke <andreas.schaelicke@helmholtz-berlin.de>
#          Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date: 2017, 2020, 2024
"""Generate the interface code for Google Protobuf

For Google protocol buffer see
https://developers.google.com/protocol-buffers
"""

import os.path
import setuptools
import logging

logger = logging.getLogger('setup')
_log = setuptools.distutils.log


class GenerateProtocolBuffer(setuptools.Command):
    """Custom build step for protobuf

    Generate the python and c++ wrapper code from the protocol buffer specifications
    """

    description = "Run protoc to generate python and cpp wrapper files"

    user_options = [
        # The format is (long option, short option, description).
        ('inplace', None, 'create files inplace of proto-file (default)'),
        ('python', None, 'create python wrapper'),
        ('cpp', None, 'create C++ wrapper'),
        ('source', None, 'files to be processed by protoc'),
        ('src-dir', None, 'directory, where the input files are located'),
        ('pydir', None, 'directroy, where the python output will be placed'),
        ('build-dir', None, 'directroy, where the output will be placed'),
        ('protoc=', None, 'protoc executable to use'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.inplace = True
        self.python = False
        self.cpp = False
        self.protoc = None
        cwd = os.getcwd()
        self.source = ''
        self.pydir = cwd
        self.src_dir = cwd
        self.build_dir = cwd
        # towards building in the temporary directory
        self.build_temp = None


    def finalize_options(self):
        """Post-process options."""
        if not self.inplace:
            self.announce('inplace False is not support yet',
                          level=_log.WARN)
            raise NotImplementedError('inplace False is not support yet')

        if not self.python and not self.cpp:
            self.python = True
            self.cpp = True
            self.announce('select python and C++ wrapper',
                          level=_log.INFO)

        self.set_undefined_options(
            'build',('build_temp', 'build_temp')
        )

    def run(self):
        self.announce(f"creating wrapper for Archiver Protocol Buffers: self.cpp = {self.cpp}",
                      level=_log.INFO)

        if self.protoc is None:
            protoc = 'protoc'
        else:
            protoc = self.protoc

        args = [protoc, self.source, '--proto_path={}'.format(self.src_dir)]

        if self.cpp:
            t_args = args + ['--cpp_out={}'.format(self.build_dir)]
            self.announce(f'Creating proto buffer using {t_args}', level=_log.INFO)
            self.spawn(t_args)
        if self.python:
            t_args = args + ['--python_out={}'.format(self.build_dir)]
            self.announce(f'Creating proto buffer using {t_args}', level=_log.INFO)
            self.spawn(t_args)

        py_file = os.path.basename(self.source).split('.proto')[0] + '_pb2.py'
        # need to hand that over to the python package builder
        self.copy_file(os.path.join(self.build_dir, py_file), 'bact_archiver')
