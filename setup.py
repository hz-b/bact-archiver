# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020

from cysetuptools import setup
import protocol_buffer

cmdclass = dict(build_proto_c=protocol_buffer.GenerateProtocolBuffer)
setup(cmdclass=cmdclass,
      author = "Andreas Schälicke, Pierre Schnizer",
      author_email = ("andreas.schälicke@helmholtz-berlin.de, "
                      "pierre.schnizer@helmholtz-berlin.de")
)
