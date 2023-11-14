"""Load archiver configuration data
"""
from .errors import DefaultArchiverNotFound
import configparser
import logging
from abc import ABCMeta, abstractmethod

logger = logging.getLogger('bact-archiver')


class ArchiverConfigurationInterface(metaclass=ABCMeta):

    @property
    @abstractmethod
    def retrieval_url(self):
        raise NotImplementedError('Derive from this class')

    @property
    @abstractmethod
    def management_url(self):
        raise NotImplementedError('Derive from this class')


class ArchiverConfiguration(ArchiverConfigurationInterface):
    """
    Args:
        name: short name or nickname of the archiver
        base_url : the base url of the archiver

    Retrieval path can be url.
    If base_url is not given, it is assumed that the retrieval path
    and management path contain the server path too.
    management_port can be only used if a base_url is given.
    """
    def __init__(self, name=None, base_url=None, retrieval_path='retrieval',
                 management_path='mgmt', management_port=17665,
                 description=""):
        """
        """
        self.name = name
        self.base_url = base_url
        self.retrieval_path = retrieval_path
        self.management_path = management_path
        self.management_port = management_port
        self.description = description

    def __repr__(self):
        args_text = "base_url={}, ".format(self.base_url)
        args_text += "retrieval_path={}, ".format(self.retrieval_path)
        args_text += "management_port={}, ".format(self.management_port)
        args_text += "management_path={}, ".format(self.management_path)
        txt = "{}({}, {})".format(self.__class__.__name__, self.name,
                                  args_text)
        return txt

    @property
    def retrieval_url(self):
        if self.base_url is not None:
            path = self.base_url + '/' + self.retrieval_path
            return path
        assert(self.retrieval_path is not None)
        return self.retrieval_path

    @property
    def management_url(self):
        if self.base_url is None:
            if self.management_port is not None:
                txt = (
                    "Management port {} but no base url is given  for archiver"
                    " {}. Do not know how to handle that!"
                ).format(self.management_path, self.name)
                raise AssertionError(txt)
            assert(self.management_path is not None)
            return self.management_path

        tmp = self.base_url, self.management_port, self.management_path
        path = "{}:{}/{}".format(tmp)
        return path


def get_config_filename(module_name: str):
    '''Get the configuration filename using pkg_resources
    '''
    from importlib.resources import files
    archiver_config_file = files(module_name).joinpath('archiver.cfg')
    logger.info('Config file expected at %s', archiver_config_file)
    return archiver_config_file


def archiver_configurations(module_name):
    '''Generates :class:`ArchiverConfiguration` from configuration file

    Args:
        module_name : the name of the module containing the archiver
                      information

    Returns:
        dictonary of archiver configurations

    Retrieves the filename in question using :func:`get_config_filename`
    The key 'default' contains the same instance, that will be given by its
    orginal name
    '''
    filename = get_config_filename(module_name=module_name)
    config = configparser.ConfigParser()
    try:
        config.read([filename])
    except Exception as exc:
        logger.error(f"Failed to read config file {filename} of {type(filename)} for {module_name}")
        raise exc


    def create_archiver(name):
        if name == "default":
            return
        kwargs = config[name]
        return ArchiverConfiguration(name=name, **kwargs)

    sections = config.sections()
    archiver_configs = {key: create_archiver(key) for key in sections}

    # Add default archiver as key default
    try:
        default_section = config['default']
    except Exception:
        txt = 'Could not find section default in file {}'.format(filename)
        txt = 'Known sections {}'.format(sections)
        logger.error(txt)
        raise

    name = default_section['name']
    try:
        default_archiver_cfg = archiver_configs[name]
    except KeyError as ke:
        txt = 'Could not find a section with name {}'.format(name)
        txt += ' known sections are {}'.format(sections)
        txt += ' archiver dic has keys {}'.format(
            list(archiver_configs.keys())
        )
        txt += ' Original exception {}'.format(ke)
        logger.error(txt)
        raise DefaultArchiverNotFound(txt)

    archiver_configs['default'] = default_archiver_cfg
    return archiver_configs
