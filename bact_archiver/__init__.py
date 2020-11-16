"""

Archivers are loaded:

   * as soon as the default archiver is accesed
   * register_archivers is called

"""

from .archiver import register_archivers
register_archivers(__name__)
