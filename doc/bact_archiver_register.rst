Registering archivers in your module
====================================

Typically it will be sufficient to

* edit `config/archiver.cfg`

* leave the following lines in `__init__.py`


.. code:: python

    from bact_archiver import register_archivers
    register_archivers(__name__)


if you modify `bact-archiver-local` to your needs. When your packages
is loaded, :func:`bact_archiver.register_archivers` will read your
configuration file. It will add each archiver it finds there to your
module using the `section name` in the configuration. Furthermore it
will add the default one as 'default'. Thus the default archiver can
be accessed by `<your-package-name>.default`.


Internals of the register module
--------------------------------

The register module is split up in different parts. These are
considered internal to the package. Please drop a line if you need
parts of this functionality exposed.

.. automodule:: bact_archiver.register
    :members:
    :undoc-members:
    :show-inheritance:
