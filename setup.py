# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020, 2023, 2024
import os
import sys

from setuptools import Extension, setup
from numpy import get_include
# required that protocol_buffer is found
sys.path.append(os.path.dirname(__file__))
from protocol_buffer import GenerateProtocolBuffer

setup(
    cmdclass=dict(build_proto_c=GenerateProtocolBuffer),
    ext_modules=[
        Extension(
            name="bact_archiver.epics_event",
            sources=[
                "proto/epics_event.pyx",
                "proto_gen/epics_event.pb.cc",
            ],
            include_dirs=[".", "proto_gen/", get_include()],
            libraries=[
                "protobuf",
            ],
            language="c++",
        )
    ],
)
