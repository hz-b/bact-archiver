# -*- coding: utf-8 -*-
# Author: Andreas Schälicke <andreas.schaelicke@helmholtz-berlin.de>
# Time-stamp: <2017-11-21 11:49:27 schaelicke>
"""Work horse access to EPICS archiver appliance
"""

from .epics_event import read_chunk, decode
from . import epics_event_pb2 as proto
from .protocol_buffer import (Chunk, dtypes as _dtypes, decoder as _decoder,
                            dbrtypes as _dbrtypes)
from .archiver import ArchiverBasis

from urllib.request import urlopen, quote, HTTPError
from functools import lru_cache

import numpy as np
import pandas as pd

import datetime
import dateutil.parser
import dateutil.tz
import enum

import logging

logger = logging.getLogger('bact-archiver')


class ApplianceOperators(enum.Enum):
    '''

    Todo:
       check: generic archiver request?
    '''
    firstSample =   'firstSample'
    lastSample =    'lastSample'
    firstFill =     'firstFill'
    lastFill =      'lastFill'
    mean =          'mean'
    min =           'min'
    max =           'max'
    count =         'count'
    ncount =        'ncount'
    nth =           'nth'
    median =        'median'
    std =           'std'
    jitter =        'jitter'
    ignoreflyers =  'ignoreflyers'
    flyers =        'flyers'
    variance =      'variance'
    popvariance =   'popvariance'
    kurtosis =      'kurtosis'
    skewness=       'skewness'


def dquote(pvname, dtype):
    if dtype == 'raw':
        return quote(pvname)
    elif dtype in appliance_operators:
        return quote('{}({})'.format(dtype, pvname))
    else:
        raise AssertionError('dtype {} unknown'.format(dtype))


def read_header(line):
    header = proto.PayloadInfo()
    header.ParseFromString(decode(line))
    return header


def read_sequence(seq):
    # separate header line
    lines = seq.split(b'\n', 1)
    chunk = Chunk(read_header(bytearray(lines.pop(0))))
    # if existing read remaining data (here the main work is done)
    for line in lines:
        chunk.value = read_chunk(bytearray(line), chunk.header)
        #print('len = ',len(chunk.value))
    return chunk


@lru_cache(maxsize=64)
def get_data(data, *, return_type='pandas', time_format='timestamp',
             padding=False, t_start=None, t_stop=None):
    #print("get_data.cache_info: {}".format(request_data.cache_info()))
    """Parses HTTP/PB data buffer

    see [HTTPPB]_

    args:
        return_type (str, optional) : requested data type (pandas|raw). Defaults to pandas
        time_format (str, optional) : requested time format (raw, timestamp, datetime). Defaults to timestamp
        padding (str, optional) : restrict timestamp to requested time range (cuts first entry and adds dummy last entry)

    The following return types are supported
        'pandas'
            pandas DataFrame

        'raw'
            tuple (header, values, secs, nanos)

    The following time formats are supported:
        'raw'
           seconds (since beginning of year), nanoseconds

        'timestamp'
           seconds since 01.01.1970 (default)

        'datetime'
           datetime object ('pandas' only)


    Returns:
        tuple of numpy arrays or pandas.DataFrame

    Example::

        with open('data.pb','rb') as f:
            header, values, seconds, nanos = get_data(f.read(), return_type='raw')
    """

    res = []
    years = []
    # ignore last '\n' and split into chunks
    for seq in data[:-1].split(b'\n\n'):
        chunk = read_sequence(seq)
        # logger.debug('chunk header "{}"'.format(chunk.header))

        if chunk.value is not None:
            # logger.debug(chunk.value)
            res.append(chunk.value)
            header = chunk.header
            years.extend(chunk.header.year *
                         np.ones(len(chunk.value[0]), dtype=np.int))
            logger.debug(chunk.header)
            # print('found data:',len(chunk.value[0]))
        else:
            pass
        #    logger.debug('no data')

    # if single chunk with data, return here
    if len(res) == 0:
        logger.error('no data received')
        return None
    elif len(res) == 1:
        values, secs, nanos = res[0]
        years = years[0] * np.ones(len(secs), dtype=np.int)
        # print('One Chunk Only')
        # print('chunk.header.year = ',chunk.header.year)
    else:
        # if multible chunks, combine data and return
        # print("{} chunks found".format(len(res)))
        values = np.concatenate([r[0] for r in res])
        secs = np.concatenate([r[1] for r in res])
        nanos = np.concatenate([r[2] for r in res])

    if return_type == 'pandas':
        if time_format == 'datetime':
            # print('creating dataframe for year', header.year)
            df = pd.DataFrame({
                'year': years,
                'month': 1,
                'day': 1,
                'second': secs,
                'ns': nanos
            })
            dt = pd.to_datetime(df, utc=True)
            dt.name = 'datetime'
            df = pd.DataFrame(values, index=dt)
            if len(df.columns) == 1:
                df.columns = ['val']

            # Code of old versin
            df = df.tz_localize('UTC').tz_convert(dateutil.tz.tzlocal())
            # python3.7 pandas 0.24.2
            # df = df.tz_convert(dateutil.tz.tzlocal())

            if padding:
                if t_start is not None and t_stop is not None and len(df.columns) == 1:
                    # move first value to start of requested time range
                    first = pd.DataFrame([df['val'][0]], columns = ["val"], index=[t_start])
                    # add dummy last value at end of requested time range
                    last = pd.DataFrame([df['val'][-1]], columns = ["val"], index=[t_stop])
                    df = pd.concat([first ,df[1:], last ])
                else:
                    raise NotImplemented('padding not implemented for non-scalars')

        elif time_format == 'raw':
            df = pd.DataFrame({'second': secs, 'ns': nanos, 'val': values})
        elif time_format == 'timestamp':
            offset = datetime.datetime(header.year,
                                       1,
                                       1,
                                       tzinfo=dateutil.tz.tzutc()).timestamp()
            # df = pd.DataFrame({'timestamp':offset+secs+1.e-9*nanos, 'val':values})
            t = pd.Series(offset + secs + 1.e-9 * nanos, name='timestamp')
            df = pd.DataFrame(values, index=t)

        df.meta = {'header': header}

        return df
    else:  # return_type=='raw'
        return (header, values, secs, nanos)


class Archiver(ArchiverBasis):
    '''Access implemented with cython and protoc compiler
    '''
    def getData(self, pvname, *, t0, t1, **kwargs):
        fmt = self.data_url_fmt
        url = fmt.format(format='raw', var=quote(pvname),
                         t0=quote(t0), t1=quote(t1))
        try:
            f = urlopen(url)
        except Exception as ex:
            logger.error('Failed to open url {}: reason {}', url, ex)
            raise ex

        x0 = dateutil.parser.isoparse(t0).astimezone(dateutil.tz.tzlocal())
        x1 = dateutil.parser.isoparse(t1).astimezone(dateutil.tz.tzlocal())
        return get_data(f.read(), t_start=x0, t_stop=x1, **kwargs)

    @lru_cache(maxsize=64)
    def requestData(self, pvname, *, t0, t1,  dtype='raw'):
        #print("request_data.cache_info: {}".format(request_data.cache_info()))
        try:
            logger.info("request_data({}...)".format(get_url()))
            request = get_url().format(format='raw',
                                       var=dquote(pvname, dtype),
                                       t0=quote(t0),
                                       t1=quote(t1))
            f = urlopen(request)
            return f.read()
        except Exception as e:
            logger.error('Failed to handle request {} reason {}'.format(request, e))
        raise e


    def guessSize(self, vname, t0, t1):

        try:
            info = self.getTypeInfo(pvname)
            has_type_info = True
        except HTTPError:
            logger.info('No Type Info')
            has_type_info = False

        if not has_type_info:
            data = self.requestData(pvname, t0, t0, dtype='firstSample')
            header, values, secs, nanos = get_data(data, return_type='raw')
            logger.debug(header)
            if header.type == 0 or header.type == 7:
                # TODO: support string types
                raise NotImplementedError('string types not supported yet')
            nbytes = np.typeDict[_dtypes[header.type]](0).nbytes
            nbytes *= header.elementCount
        else:
            count = int(info['elementCount'])
            dbrtype = info['DBRType'].split('_')[2]
            #print(dbrtype)
            if dbrtype in ['STRING']:
                # TODO: support string types
                raise NotImplementedError('string types not supported yet')
            else:
                nbytes = _dsize[_dbrtypes[dbrtype]] * count
                #print(count,nbytes)

        data = self.requestData(pvname, t0, t1, dtype='ncount')
        header, values, secs, nanos = get_data(data, return_type='raw')
        ncount = values[0]
        return (ncount, nbytes)
