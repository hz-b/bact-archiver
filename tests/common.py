# Author: Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date: Sep. 2017
from __future__ import absolute_import, print_function, division
import os.path

_dir_name = os.path.dirname(__file__)
test_data_dir = os.path.join(_dir_name, "test_data")
test_data_dir = os.path.normpath(test_data_dir)
