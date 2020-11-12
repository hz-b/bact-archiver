# -*- coding: utf-8 -*-
# Author: Andreas Schälicke <andreas.schaelicke@helmholtz-berlin.de>
#          Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Date: 2017
"""Single stop point for config

It provides the possibility to write defines to a config.h file next to
the possibilites for storing this information in a config.py file
"""
import copy
import os.path

# Could not find a config command in setuptools
from distutils.command import config
import setuptools

_log = setuptools.distutils.log

_config_file_name_prefix = "bact_archiver_config_features"

#: c header file containing defines of the type
#:  ``BACT_HAVE_`` with the tested macro at the lines afterwards
config_header_file_name = _config_file_name_prefix + os.path.extsep + "h"


#: python file containing defines of the type
#: ``have_``
config_file_name =  _config_file_name_prefix + os.path.extsep + "py"

# The python import module name
config_module = _config_file_name_prefix


class BactConfig(config.config):
    """Find configurations and write them to the different files

    The target is to have a single feature and configuration file. Thus the
    derived classes shall implement a :attr:`run_config`

    After all subclasses have been executed, the configuration file will be
    written
    """
    #--------------------------------------------------------------------------
    # Part expected to be used by derived classes
    def check_macro_in_header(self, macro_name, *args, **kws):
        """Check that a macro exists in the header. If it exists store that in
        the default config header file

        Args:
             macro_name : the macro name to test for

        All additional arguments and keywords are passed to :func:`check_func`
        See :class:`distutils.command.config.config`  for details
        """

        flag = self.check_func(macro_name, *args, **kws)

        config_name = "BACT_HAVE_" + macro_name
        self._add_tested_configuration_macro(config_name, flag)

        return flag

    def add_tested_feature(self, var_name, val):
        """In the configuration file var_name will be set to val

        Args:
            var_name : the variable name
            val : the value the variable shall be set to
        """
        return self._add_tested_configuration_dic(self._bact_config_features,
                                                  var_name, val)

    def write_configurations_to_file(self):
        """Write the configurations to the c header file and to the python file

        WARNING:
             This function must be called by the user at the end of all
             configuration processes
        """
        self.write_config_file()
        self.write_header_file()

    def run_config(self):
        """This method shall be implemented in the derived classes
        """
        raise ValueError("Base class: should be subclassed")

    #--------------------------------------------------------------------------
    _bact_config_macros = {}
    _bact_config_features = {}

    def run(self):
        """The actual execution

        Currnently only subclassed by prototype_buffer_config

        TODO:
             reimplement if more configuration classes are added.
             Target: have a single header and python file showing the found
             features
        """
        self.run_config()
        self.write_configurations_to_file()

    #--------------------------------------------------------------------------
    # Internal functions. Not expected to be used by derived classes
    def _add_tested_configuration_dic(self, config_dic, macro_name, val):
        # Test that the key does not yet exist
        test = False
        try:
            config_dic[macro_name]
            test = True
        except KeyError:
            pass

        if test is not False:
            msg = "macro '%s' already defined in the config macros dictonary"
            raise ValueError(msg % (macro_name))

        config_dic[macro_name] = val

    def _add_tested_configuration_macro(self, macro_name, val):
        return self._add_tested_configuration_dic(self._bact_config_macros,
                                                  macro_name, val)


    def get_config_dir(self):
        t_dir = os.path.dirname(__file__)
        return t_dir

    def write_config_file(self):
        """Write the configuration options to a single python file

        This file is installed in the bact code. It shall be available so that
        the run code can switch between different implementations.
        """
        config_dic = self._bact_config_features
        keys = config_dic.keys()
        keys = copy.copy(list(keys))
        keys.sort()

        txt="""'''BACT configuration file

WARNING:
      This file was generated during the configuration (build) process.
      Please edit "%s" instead!
'''
"""

        t_dir = self.get_config_dir()
        # config_file = os.path.join(t_dir, os.pardir, "bact", config_file_name)
        config_file = os.path.join(t_dir, config_file_name)
        config_file = os.path.normpath(config_file)
        self.announce("Writing configuration file %s" %(config_file,),
                      level=_log.INFO)
        with open(config_file, "wt") as config_file:
            config_file.write(txt % (__file__,))

            for key in keys:
                val = config_dic[key]
                config_file.write("%s = %s\n" %(key, val))

    def write_header_file(self):
        """Write different configuration options to a single header file
        """

        config_dic = self._bact_config_macros
        keys = config_dic.keys()
        keys = copy.copy(list(keys))
        keys.sort()

        t_dir = self.get_config_dir()
        config_file = os.path.join(t_dir, config_header_file_name)
        with open(config_file, "wt") as config_header:


            header_enclosing_macro = "_BACT_CONFIG_H_"
            # header
            txt="""/*----------------------------------------------------------------------
 *
 * WARNING:  This file was generated during the configuration (build) process.
 *           Please edit "%s" instead!
 *
 ----------------------------------------------------------------------*/
#ifndef %s
#define %s 1
"""
            tmp = (__file__,) + (header_enclosing_macro,)*2
            config_header.write(txt % tmp)
            for key in keys:
                val = config_dic[key]
                if val == False:
                    val = 0
                elif val == True:
                    val = 1
                else:
                    # Currently no other "c compatible conversions considered"
                    pass
                txt = "#define %s %s" %(key, val)
                if val:
                    config_header.write(txt+ "\n")
                else:
                    config_header.write("/* %s */\n" % (txt,))
            # footer
            config_header.write("#endif /* %s */\n/* EOF */\n" %(header_enclosing_macro,))
