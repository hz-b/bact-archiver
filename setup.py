# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020
# import logging
# logging.basicConfig(level=logging.DEBUG)
# import sys
# import os.path
# import importlib

from cysetuptools import setup
import setuptools
import prototype_buffer

print(prototype_buffer.GenerateProtocolBuffer.user_options)
cmdclass = dict(build_proto_c=prototype_buffer.GenerateProtocolBuffer)

#--- load extra command module
#------------------------------------------------------------------------------

setup(cmdclass=cmdclass)

# setup(
#     fullname = "BACT epics archiver appliance access ",
#     name = "bact-archiver",
#     version = "0.0.0",
#     author = "Andreas Schälicke, Pierre Schnizer",
#     author_email= "andreas.schaelicke@helmholtz-berlin.de, pierre.schnizer@helmholtz-berlin.de",
#     description = desc,
#     license = "GPL",
#     keywords = "EPICS",
#     url="https://github.com/hz-b/bact-archiver",
#     packages = packages,
#     # proto_modules = backend,
#     cythonize=False,
#     # cmdclass = cmdclass,
#     classifiers = [
#     ]
# )
