Configuring bact archiver
=========================

This packages contains the code implementing the protobuf based
protocol. For adaption to local installation it is recommended
to create a package like e.g. http:pypi.org//bact-archiver-bessyii.

Apart from files required by setup, this packages contains two files:

    `config/archiver.cfg`
        access information to the available archivers

    `__init__.py`:
        executes register function from bact-archiver


Format of `config/archiver.cfg`
-------------------------------
The default section contains the name of the archivers, that should be
your default archiver. Apart from the default section, each section
reflects the access to an archiver appliance. Each entry matches
one keyword of the initaliser of
:class:`bact_archiver.config.ArchiverConfiguration`.



Configuration Classes
---------------------

.. autoclass:: bact_archiver.config.ArchiverConfigurationInterface
    :members:
    :undoc-members:
    :show-inheritance:


.. autoclass:: bact_archiver.config.ArchiverConfiguration
    :members:
    :undoc-members:
    :show-inheritance:
