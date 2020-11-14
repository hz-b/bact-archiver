# -*- coding: utf-8 -*-
# Author: Andreas Schälicke <andreas.schaelicke@helmholtz-berlin.de>
# Time-stamp: <2017-11-21 10:21:24 schaelicke>

from . import epics_event_pb2 as proto
from urllib.request import urlopen, quote, HTTPError
import numpy as np
import h5py
import json

_url = None
_url_bpl = None

archivers = {
    "AAPL": {
        "retr_url": "http://archiver.trs.bessy.de/retrieval/",
        "mgmt_url": "http://archiver.trs.bessy.de:17665/mgmt/",
        "descr": "central BESSY archiver",
    },
    "BESSY": {
        "retr_url": "http://archiver.trs.bessy.de/retrieval/",
        "mgmt_url": "http://archiver.trs.bessy.de:17665/mgmt/",
        "descr": "central BESSY archiver",
    },
    "FASTZC": {
        "retr_url": "http://fastzc.ctl.bessy.de/retrieval/",
        "mgmt_url": "http://fastzc.ctl.bessy.de:17665/mgmt/",
        "descr": "Fast Short Term Archiver inside BESSY Control System",
    },
    "FASTZC proxy": {
        "retr_url": "http://archiver.bessy.de/FASTZC/",
        "mgmt_url": None,
        "descr": "Fast Short Term Archiver through Proxy",
    },
    "MLS": {
        "retr_url": "http://arc41cp.mlscs.bessy.de/retrieval/",
        "mgmt_url": "http://arc41cp.mlscs.bessy.de:17665/mgmt/",
        "descr": "MLS Archiver - direct access"
    },
    "MLS proxy": {
        "retr_url": "http://archiver.bessy.de/MLSAAPL/retrieval/",
        "mgmt_url": None,
        "descr": "MLS Archiver"
    },
}

archiver_request_fmt = "%Y-%m-%dT%H:%M:%S.000000Z"
def convert_datetime_to_timestamp(datum):
    return datum.strftime(archiver_request_fmt)



def set_archiver_url(arch):
    global _url, _url_bpl
    # print("switching to %s: %s" % (arch, archivers[arch]))
    _url = archivers[arch]["retr_url"] + "data/getData.{format}?pv={var}&from={t0}&to={t1}&ca_how=0"
    _url_bpl = archivers[arch]["retr_url"] + "bpl/{cmd}{opt}"


def get_url():
    return _url


# restore old default behaviour - should better be 'AAPL' in the future
set_archiver_url('AAPL')


class Chunk(object):
    def __init__(self, header):
        self.header = header
        self.events = []
        self.meta = None
        self.value = None

    def add(self, event):
        self.events.append(event)


# select protocol buffer decoder for EPICS type
_decoder = {
    0: proto.ScalarString,
    1: proto.ScalarShort,
    2: proto.ScalarFloat,
    3: proto.ScalarEnum,
    4: proto.ScalarByte,
    5: proto.ScalarInt,
    6: proto.ScalarDouble,
    7: proto.VectorString,
    8: proto.VectorShort,
    9: proto.VectorFloat,
    10: proto.VectorEnum,
    11: proto.VectorChar,
    12: proto.VectorInt,
    13: proto.VectorDouble,
    14: proto.V4GenericBytes
}

# translate EPICS types to numpy types
_dtypes = {
    0: 'S40',
    1: 'i2',
    2: 'f4',
    3: 'u4',
    4: 'b1',
    5: 'i4',
    6: 'f8',
    7: 'str',
    8: 'i2',
    9: 'f4',
    10: 'u4',
    11: 'b1',
    12: 'i4',
    13: 'f8'
}

_dsize = {
    0: 40,
    1: 2,
    2: 4,
    3: 4,
    4: 1,
    5: 4,
    6: 8,
    7: 40,
    8: 2,
    9: 4,
    10: 4,
    11: 1,
    12: 4,
    13: 8
}

_dbrtypes = {
    'STRING': 0,
    'INT': 1,
    'SHORT': 1,
    'FLOAT': 2,
    'ENUM': 3,
    'CHAR': 4,
    'LONG': 5,
    'DOUBLE': 6
}


class ArchiverRequest(object):
    def __init__():
        pass


# Note: This is UTC time format!
def archiver(var, t0='2017-10-02T21:00:00.000Z',
             t1='2017-10-02T21:10:00.000Z'):
    """
    valid ISO 8601 time formats are :
     2017-09-01T00:02:00Z
     2017-09-01T00:02:00.000Z
     2017-09-01T00:00:00+02
     2017-09-01T00:00:00+0200
     2017-09-01T00:00:00+02:00
     2017-09-01T00:00:00.000+02:00
    """
    f = urlopen(
        _url.format(format='raw', var=quote(var), t0=quote(t0), t1=quote(t1)))

    return get_data(f.read())


def ask_appliance(cmd, **kw):
    # cmds :
    opts = ''
    opt = '?{}={}'
    for k, v in kw.items():
        opts += opt.format(k, v)
        opt = '&{}={}'
    url = _url_bpl.format(cmd=cmd, opt=opts)
    print(url)
    request = urlopen(url)
    data = json.loads(request.read().decode('UTF-8'))
    return data


def get_allPVs():
    return get_matchingPVs()


def get_matchingPVs(pv="*"):
    return ask_appliance('getMatchingPVs', pv=pv)


def get_typeInfo(pv):
    return ask_appliance('getMetadata', pv=pv)


def get_data(data):
    chunks = []
    for seq in data.split(b'\n\n'):
        lines = seq.splitlines()

        header = proto.PayloadInfo()
        header.ParseFromString(
            lines.pop(0).replace(b'\x1b\x02', b'\x0a').replace(
                b'\x1b\x03', b'\x0d').replace(b'\x1b\x01', b'\x1b'))
        chunk = Chunk(header)
        chunks.append(chunk)

        dtype = _dtypes[header.type]

        if 7 <= header.type <= 13:
            # vector decoder
            def parse_vec(inp, event=_decoder[header.type]()):
                event.ParseFromString(
                    inp.replace(b'\x1b\x02', b'\x0a').replace(
                        b'\x1b\x03', b'\x0d').replace(b'\x1b\x01', b'\x1b'))
                return [v
                        for v in event.val], event.secondsintoyear, event.nano

            chunk.values = np.array(
                [parse_vec(l) for l in lines],
                dtype=[('value', dtype, (header.elementCount, )),
                       ('sec', 'u4'), ('ns', 'u4')])
        else:
            # scalar decoder
            def parse(inp, event=_decoder[header.type]()):
                event.ParseFromString(
                    inp.replace(b'\x1b\x02', b'\x0a').replace(
                        b'\x1b\x03', b'\x0d').replace(b'\x1b\x01', b'\x1b'))
                return event.val, event.secondsintoyear, event.nano

            chunk.values = np.array(
                [parse(l) for l in lines],
                dtype=[('value', dtype), ('sec', 'u4'), ('ns', 'u4')])

    return header, np.concatenate([c.values for c in chunks])


def save_pbraw(var,
               t0='2017-10-02T21:00:00.000Z',
               t1='2017-10-02T21:10:00.000Z',
               *,
               fname='test.pb'):
    f = urlopen(
        _url.format(format='raw', var=quote(var), t0=quote(t0), t1=quote(t1)))

    with open(fname, 'wb') as fout:
        fout.write(f.read())


def save_hdf5(data, *, fname=None):
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
