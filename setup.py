# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020, 2023, 2024

import sys
import os.path
# required that cysetuptools is found
sys.path.append(os.path.dirname(__file__))

from cysetuptools import setup
import protocol_buffer
from setuptools.command.build_ext import build_ext


class ProtoBufferBeforeBuild(build_ext):
    """Currently always run protoc before building extensions"""
    sub_commands = [("build_proto_c", None)] + build_ext.sub_commands


cmdclass = dict(
    build_proto_c=protocol_buffer.GenerateProtocolBuffer,
    build_ext=ProtoBufferBeforeBuild
)

setup(
    cmdclass=cmdclass,
    author="Andreas Schälicke, Pierre Schnizer",
    author_email=(
        "andreas.schälicke@helmholtz-berlin.de", "pierre.schnizer@helmholtz-berlin.de"
    ),
)
