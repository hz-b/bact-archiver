# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020, 2023, 2024

import sys
import os.path

# required that cysetuptools is found
sys.path.append(os.path.dirname(__file__))

from cysetuptools import setup
from setuptools.command.build import build
from setuptools import distutils
import protocol_buffer


class ActionOnBuild(build):
    def __init__(self, dist, **kwargs):
        build.__init__(self, dist, **kwargs)
        # just default args
        self._build_proto_c = protocol_buffer.GenerateProtocolBuffer(dist)

    def run(self):
        self.announce(
            "Building archiver: creating protocol buffer", level=distutils.log.INFO
        )
        self._build_proto_c.run()
        self.announce(
            "Building archiver: running standard build", level=distutils.log.INFO
        )
        build.run(self)


cmdclass = dict(
    build_proto_c=protocol_buffer.GenerateProtocolBuffer, build=ActionOnBuild
)

setup(
    cmdclass=cmdclass,
    author="Andreas Schälicke, Pierre Schnizer",
    author_email=(
        "andreas.schälicke@helmholtz-berlin.de, " "pierre.schnizer@helmholtz-berlin.de"
    ),
)
