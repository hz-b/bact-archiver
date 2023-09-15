"""Access to archivers: code part

As user typically:

* get the source of bact-archiver-local
* rename it (e.g. for PSI bact-archiver-psi)
* edit config/archiver.cfg to reflect your achivers

Install your local package. This will install this package
in turn. See installation and configuration information in
packages documentation
"""

# the config packages expect to find this function
from .register import register_archivers

# No archivers here in this package
# Put this call in your local package
# register_archivers(__name__)


__all__ = ["utils"]
