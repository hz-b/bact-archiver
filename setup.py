# -*- coding: utf-8 -*-
# Authors : Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
#           Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date : 2017, 2020
from __future__ import print_function

import sys
import os.path
import importlib

from setuptools import setup
import setuptools

#------------------------------------------------------------------------------
# Handle configuration
# Build extensions in directory  bact_dist
# still required?
_t_dir = os.path.dirname(__file__)
_dist_dir =  "dist_bact_archiver"
sys.path.insert(0, os.path.join(_t_dir, _dist_dir))


_config_rerun = "%s %s config" %(sys.executable, __file__)
import bact_archiver_config
# Check if configuration was executed
try:
    #print("Checking for confguration file %s" %(bact_config.config_module,))
    importlib.import_module(bact_archiver_config.config_module)
except ImportError:
    if "config"  not in sys.argv:
        print("Please run first: " + _config_rerun)
        sys.exit()
    has_config = False
else:
    has_config = True

if has_config == True:
    # Up to now only python file was checked. A c header file shall exist too
    c_header_file = os.path.join(_t_dir, _dist_dir,
                                 bact_archiver_config.config_header_file_name)
    if not os.path.exists(c_header_file):
        print("C header file creation '%s' failed! Please (re)run %s" %
              (c_header_file ,_config_rerun))
        sys.exit()

del _t_dir, _config_rerun

#------------------------------------------------------------------------------
# The part independent of any configuration options
import prototype_buffer_config

cmdclass =     {
        'config' : prototype_buffer_config.ConfigProtoBuf,
}

cython_extensions = []
#------------------------------------------------------------------------------
# The part dependent on configuration options
if has_config:
    import prototype_buffer
    cython_extensions += prototype_buffer.cython_extensions
    cmdclass['build_proto'] = prototype_buffer.GenProtobuf

#------------------------------------------------------------------------------
# info provided to setup()
packages = setuptools.find_packages()
desc ="""EPICS archiver appliance access using google protobuf
"""

# Currently all extension modules as cython extensions
ext_modules = cython_extensions + []

setup(
    fullname = "Berlin accelerator commissioning tools",
    name = "bact-archiver",
    version = "0.0.0",
    author = "Andreas Schälicke, Pierre Schnizer",
    author_email= "pierre.schnizer@helmholtz-berlin.de andreas.schaelicke@helmholtz-berlin.de",
    description = desc,
    license = "GPL",
    keywords = "EPICS",
    url="https://github.com/hz-b/bact-archiver",
    packages = packages,
    ext_modules = ext_modules,
    cmdclass = cmdclass,
    classifiers = [
        "Development Status :: 2 - Pre - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ]
)
