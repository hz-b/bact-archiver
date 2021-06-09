class DefaultArchiverNotFound(Exception):
    '''Default archiver was not found.

    Typically raised:

    The configuration file is read. In the default section the
    default archiver is named but no section in the configuration
    file uses the same name.
    '''


class ArchiverReturnedNoData(Exception):
     '''Arichver returned no data for valid request

     Typically raised:
           Request is accepted but no data were returned.
     '''
