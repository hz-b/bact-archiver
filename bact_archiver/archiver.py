'''Access to the epics archiver appliance

Typical usage:
     * Download package bact-archiver-local
     * Edit the archiver.cfg package there to reflect your installation
     * Installing this package will automatically install this package
'''

from abc import ABCMeta, abstractmethod, abstractproperty
import json
import logging
from urllib.request import urlopen, quote


logger = logging.getLogger('bact-archiver')


#: The format as requested by the archiver
archiver_request_fmt = "%Y-%m-%dT%H:%M:%S.000000Z"


def convert_datetime_to_timestamp(datum):
    '''Convert datetime to string as expected by archiver

    Args:
        datum: a :class:`datetime.datetime` object
    '''
    try:
        r = datum.strftime(archiver_request_fmt)
    except Exception:
        logger.error('Failed converting %s of type %s to timestamp string',
                     datum, type(datum))
        raise
    return r


class ArchiverInterface(metaclass=ABCMeta):
    '''Archiver interface definition
    '''
    @abstractproperty
    def name(self):
        'Name of the archiver'

    @abstractproperty
    def description(self):
        'Description of the archiver'

    @abstractmethod
    def getData(self, var, * t0, t1, **kws):
        """Get archiver data for single EPICS variable in given time frame.

        Args:
            t0 :                         start time a :class:`datetime.datetime` object
            t1 :                         end time a :class:`datetime.datetime` object

            return_type (str, optional) : requested data type (pandas|raw).
                                          Defaults to pandas
            time_format (str, optional) : requested time format (raw, timestamp, datetime).
                                          Defaults to timestamp
            padding (str, optional) :    restrict timestamp to requested time range
                                         (cuts first entry and adds dummy last entry)

        Returns:
            tuple of numpy arrays or pandas.DataFrame see :func:`get_data`

        The following return types are supported
            'pandas'
                a :class:`pandas.DataFrame`

            'raw'
                tuple (header, values, secs, nanos)

        The following time formats are supported:
            'raw'
               seconds (since beginning of year), nanoseconds

            'timestamp'
               seconds since 01.01.1970 (default)

            'datetime'
               datetime object ('pandas' only)

        Example::

            t0 = datetime.datetime(2017, 10, 02, 21)
            t1 = datetime.datetime(2017, 10, 02, 21, 5)
            df = archiver.getData('TOPUPCC:rdCur', t0=t0, t1=t1,
                                  return_type='pandas', time_format='datetime')
            print(df.meta['header'])
            plot(df.index, df.values.flatten())
        """
        raise NotImplementedError('Implement in derived class')

    # def __call__(self, t0, t1, **kwargs):
    #    "I am not supporting to implement this method"
    #    return self.getData(t0, t1, **kwargs)


class ArchiverBasis(ArchiverInterface):
    '''

    Warning:
        Work in progress

    Used for the python or the carchiver
    '''
    def __init__(self, *, config):
        self.config = config

    @property
    def name(self):
        return self.config.name

    @property
    def description(self):
        return self.config.description

    @property
    def data_url_fmt(self):
        url = self.config.retrieval_url
        url += "/data/getData.{format}?pv={var}&from={t0}&to={t1}&ca_how=0"
        return url

    @property
    def bpl_url_fmt(self):
        '''

        Todo: better naming?
        '''
        url = self.config.retrieval_url
        url += '/bpl/{cmd}{opt}'
        return url

    def getData(self, pvname, *, t0, t1, **kws):
        t0_str = convert_datetime_to_timestamp(t0)
        t1_str = convert_datetime_to_timestamp(t1)
        fmt = 'Trying to get data for pv %s in interval %s..%s = %s..%s',
        logger.info(fmt, pvname, t0, t1, t0_str, t1_str)

        return self._getData(pvname, t0=t0_str, t1=t1_str, **kws)

    def askAppliance(self, cmd, **kwargs):
        '''
        '''
        # cmds :
        opts = ''
        opt = '?{}={}'
        for k, v in kwargs.items():
            opts += opt.format(k, v)
            opt = '&{}={}'

        fmt = self.bpl_url_fmt
        url = fmt.format(cmd=cmd, opt=opts)
        fmt = 'Asking archiver %s  using url %s'

        logger.info(fmt, self.name, url)
        try:
            request = urlopen(url)
        except Exception as ex:
            logger.error(fmt + ' Reason %s', self.name, url, ex)
            raise ex

        data = json.loads(request.read().decode('UTF-8'))
        return data

    def getAllPVs(self):
        return self.getMatchingPVs()

    def getMatchingPVs(self, pv="*"):
        return self.askAppliance('getMatchingPVs', pv=pv)

    def getTypeInfo(self, pv):
        return self.askAppliance('getMetadata', pv=pv)

    def __repr__(self):
        args_text = 'config={}'.format(self.config)
        txt = "{}({}, {})".format(self.__class__.__name__, self.name,
                                  args_text)
        return txt

    def saveBPRaw(self, pvname, *,  t0, t1, fname='test.pb'):
        fmt = self.data_url_fmt
        url = fmt.format(format='raw', var=quote(pvname),
                         t0=quote(t0), t1=quote(t1))
        f = urlopen(url)

        with open(fname, 'wb') as fout:
            fout.write(f.read())


def save_hdf5(data, *, fname=None):
    import h5py
    chunk = data.chunks[1]
    values = data.values

    with h5py.File(fname, 'w') as f:
        group = f.create_group(chunk.header.pvname)
        group.create_dataset(
            'value', data=values['value'], compression='gzip', shuffle=True)
        group.create_dataset(
            'sec', data=values['sec'], compression='gzip', shuffle=True)
        group.create_dataset(
            'ns', data=values['ns'], compression='gzip', shuffle=True)
