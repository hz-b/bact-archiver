import sys
import logging
from .config import archiver_configurations
from .pyarchiver import Archiver
from .carchiver import Archiver

logger = logging.getLogger('bact-archiver')


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
