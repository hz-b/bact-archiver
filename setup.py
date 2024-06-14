# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020, 2023, 2024

from setuptools import Extension, setup
from numpy import get_include

setup(
    ext_modules=[
        Extension(
            name="bact_archiver.epics_event",
            sources=[
                "bact_archiver/proto/epics_event.pyx",
                "bact_archiver/proto/epics_event.pb.cc",
            ],
            include_dirs=[".", get_include()],
            libraries=[
                "protobuf",
            ],
            language="c++",
        )
    ],
)
