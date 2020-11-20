"""

Archivers are loaded:

   * as soon as the default archiver is accesed
   * register_archivers is called

"""

from .register import register_archivers
register_archivers(__name__)
