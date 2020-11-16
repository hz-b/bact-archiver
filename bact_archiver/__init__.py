"""

Archivers are loaded:

   * as soon as the default archiver is accesed
   * register_archivers is called

"""

from .register import register_archivers
register_archivers(__name__)


#: The format as requested by the archiver
archiver_request_fmt = "%Y-%m-%dT%H:%M:%S.000000Z"


def convert_datetime_to_timestamp(datum):
    '''Convert datetime to string as expected by archiver
    '''
    return datum.strftime(archiver_request_fmt)
