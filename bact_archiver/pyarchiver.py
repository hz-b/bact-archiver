# -*- coding: utf-8 -*-
# Author: Andreas Schaelicke <andreas.schaelicke@helmholtz-berlin.de>
#         Pierre Schnizer <pierre.schnizer@helmholtz-berlin.de>
# Time-stamp:
"""Archiver interface pythonic version

"""
from .archiver import ArchiverBasis
from .protocol_buffer import Chunk, dtypes as _dtypes, decoder as _decoder
from . import epics_event_pb2 as proto

from urllib.request import urlopen, quote
import numpy as np


class Archiver(ArchiverBasis):
    def getData(self, pvname, *, t0, t1, **kwargs):
        fmt = self.data_url_fmt
        url = fmt.format(format='raw', var=quote(pvname),
                         t0=quote(t0), t1=quote(t1))
        f = urlopen(url)
        data = get_data(f.read())
        return data


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
