# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020, 2023, 2024

from setuptools import Extension, setup
from setuptools_protobuf import Protobuf
from numpy import get_include

setup(
    author="Andreas Schälicke, Pierre Schnizer",
    author_email=(
        "andreas.schälicke@helmholtz-berlin.de",
        "pierre.schnizer@helmholtz-berlin.de"
    ),
    protobufs=[Protobuf("proto/epics_event.proto")],
    ext_modules=[Extension(
        name="bact_archiver.epics_event",
        sources=["proto/epics_event.pyx", "proto/epics_event.pb.cc"],
        include_dirs=[".", get_include()],
        libraries=["protobuf", ],
        language="c++"
    )],
)
