# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020

from cysetuptools import setup
import setuptools
import prototype_buffer

cmdclass = dict(build_proto_c=prototype_buffer.GenerateProtocolBuffer)
setup(cmdclass=cmdclass)
