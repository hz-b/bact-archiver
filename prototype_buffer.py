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
        ('source', None, ''),
        ('dir', None, '.'),
        ('protoc=', None, 'protoc executable to use'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.inplace = True
        self.python = False
        self.cpp = False
        self.protoc = None
        self.source = ''
        self.dir = '.'

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

        if self.protoc is None:
            protoc = 'protoc'
        else:
            protoc = self.protoc

        #self.announce('using protoc "%s"' %(protoc,), level=_log.INFO)
        args = [protoc, self.source, '--proto_path={}'.format(self.dir)]

        if self.cpp:
            self.spawn(args + ['--cpp_out={}'.format(self.dir)])
        if self.python:
            self.spawn(args + ['--python_out={}'.format(self.dir)])
