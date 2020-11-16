"""Access to the epics archiver appliance

Typical usage:
     * Download package bact-archiver-local
     * Edit the archiver.cfg package there to reflect your installation
     * Installing this package will automatically install this package
"""

from .config import archiver_configurations
import logging
import sys

logger = logging.getLogger('bact-archiver')


class Archiver:
    '''

    Warning:
        Work in progress
    '''
    def __init__(self, *, config):
        self.config = config

    @property
    def name(self):
        return self.config.name

    @property
    def description(self):
        return self.config.description

    def __repr__(self):
        args_text = 'config={}'.format(self.config)
        txt = "{}({}, {})".format(self.__class__.__name__, self.name,
                              args_text)
        return txt


def add_archivers_to_module(mod_name, configs):
    '''
    Args:
        mod_name: the name of the module to which the archivers
                  should be added.
        configs:  sequencee of archiver configurations

    each archiver configuration should conform to the interface
    defined by
    :class:`bact_archiver.config,ArchiverConfigurationInterface`
    '''

    t_mod = sys.modules[mod_name]
    logger.info('Adding archivers %s to mod %s', list(configs.keys()), t_mod)

    archivers = {tup[0]: Archiver(config=tup[1]) for tup in configs.items()}
    setattr(t_mod, 'archivers', archivers)
    for name, ac in archivers.items():
        setattr(t_mod, name, ac)


def register_archivers(module_name):
    '''Register the archivers to the module
    '''
    configs = archiver_configurations(module_name)
    add_archivers_to_module(module_name, configs)
