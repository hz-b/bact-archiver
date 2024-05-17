# -*- coding: utf-8 -*-
# Author: Andreas Schälicke <andreas.schaelicke@helmholtz-berlin.de>
#          Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date: 2017, 2020, 2024
"""Generate the interface code for Google Protobuf

For Google protocol buffer see
https://developers.google.com/protocol-buffers
"""

import os.path
from distutils.dep_util import newer_group

from setuptools import distutils, Command
from setuptools.command.build import build
from setuptools.command.build_ext import build_ext

_log = distutils.log


class GenerateProtocolBuffer(Command):
    """Custom build step for protobuf

    Generate the python and c++ wrapper code from the protocol buffer specifications
    """

    description = "Run protoc to generate python and cpp wrapper files"

    user_options = [
        # The format is (long option, short option, description).
        ("inplace", None, "create files inplace of proto-file (default)"),
        ("python", None, "create python wrapper"),
        ("cpp", None, "create C++ wrapper"),
        ("source", None, "files to be processed by protoc"),
        ("src-dir", None, "directory, where the input files are located"),
        ("build-dir",   None, "directory, where the output will be placed (within build_temp)"),
        ("protoc=", None, "protoc executable to use"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.inplace = True
        self.python = False
        self.cpp = False
        self.protoc = None
        cwd = os.getcwd()
        self.source = ""
        self.pydir = cwd
        self.src_dir = cwd
        # towards building in the temporary directory
        self.build_temp = None
        self.build_dir = None

    def finalize_options(self):
        """Post-process options."""
        if not self.inplace:
            self.announce("inplace False is not support yet", level=_log.WARN)
            raise NotImplementedError("inplace False is not support yet")

        if not self.python and not self.cpp:
            self.python = True
            self.cpp = True
            self.announce("select python and C++ wrapper", level=_log.INFO)

        self.build_dir = self.build_dir or "proto"
        self.set_undefined_options("build", ("build_temp", "build_temp"))

    def run(self):
        self.announce(
            f"creating wrapper for Archiver Protocol Buffers: self.cpp = {self.cpp}",
            level=_log.DEBUG,
        )

        if self.protoc is None:
            protoc = "protoc"
        else:
            protoc = self.protoc

        build_temp = os.path.join(self.build_temp, self.build_dir)
        self.mkpath(build_temp)

        args = [protoc, f"-I{self.src_dir}", self.source]
        source_file = os.path.join(self.src_dir, self.source)
        base_name = os.path.basename(self.source).split(".proto")[0]
        if self.cpp:
            target = os.path.join(build_temp, base_name + ".pb.cc")
            t_args = args + ["--cpp_out={}".format(build_temp)]

            if newer_group([source_file], target):
                self.announce(
                    f"target {target} out of date"
                    f"Creating proto buffer using {t_args}",
                    level=_log.DEBUG,
                )
                self.spawn(t_args)

        if self.python:
            target = os.path.join(build_temp, base_name + "_pb2.py")
            t_args = args + ["--python_out={}".format(build_temp)]
            if newer_group([source_file], target):
                self.announce(f"Creating proto buffer using {t_args}", level=_log.DEBUG)
                self.spawn(t_args)

                py_file = os.path.basename(self.source).split(".proto")[0] + "_pb2.py"
                # need to hand that over to the python package builder
                self.copy_file(os.path.join(build_temp, py_file), "bact_archiver")


class ProtoBufferBeforeBuild(build):
    """Currently always run protoc before building extensions"""

    def run(self):
        super().run()

    sub_commands = [("build_proto_c", None)] + build.sub_commands


class AddTemporaryFilesToBuildExt(build_ext):
    def initialize_options(self):
        super().initialize_options()
        self.build_dir = None

    def finalize_options(self):
        super().finalize_options()
        self.set_undefined_options("build_proto_c", ("build_dir", "build_dir"))

    def run(self):
        proto_dir = os.path.join(self.build_temp, self.build_dir)
        for ext in self.extensions:
            ext.include_dirs += [proto_dir]
            ext.sources += [os.path.join(proto_dir, ext.name.split(".")[-1] + ".pb.cc")]
        super().run()
