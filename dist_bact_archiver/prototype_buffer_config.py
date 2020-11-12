import setuptools
import bact_archiver_config
from distutils.command import config

_log = setuptools.distutils.log


class ConfigProtoBuf(bact_archiver_config.BactConfig):
    """Find out if the protocol buffer c++-library is available
    """

    def _check_google_prototype_header(self):
        """If GOOGLE_PROTOBUF_VERSION is defined at least the header files should be found.

        Currently is assumed the library then does not need to be searched
        separately
        """
        header = "google/protobuf/stubs/common.h"
        headers = [header]

        self.announce('Checking for google protobuf c library',
                      level=_log.INFO)
        kws = {"headers": headers}

        # Too soft check: works on windows machine ....
        # where it finds the header I don't know
        # val = self.check_header(header)
        val = self.check_macro_in_header("GOOGLE_PROTOBUF_VERSION", **kws)
        self.add_tested_feature("google_protobuf_c_library", val)

    def run_config(self):
        self._check_google_prototype_header()

    def check_func(self, func, headers=None, include_dirs=None,
                   libraries=None, library_dirs=None, decl=0, call=0,
                   lang="c++"):
        """Copy of config.check_func

        Required as lang can not be specified for check_func
        """
        self._check_compiler()
        body = []
        if decl:
            body.append("int %s ();" % func)
        body.append("int main () {")
        if call:
            body.append("  %s();" % func)
        else:
            body.append("  %s;" % func)
        body.append("}")
        body = "\n".join(body) + "\n"

        return self.try_link(body, headers, include_dirs,
                             libraries, library_dirs, lang=lang)
