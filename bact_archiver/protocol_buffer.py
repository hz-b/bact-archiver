from . import epics_event_pb2 as proto

#: select protocol buffer decoder for EPICS type
decoder = {
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

#: translate EPICS types to numpy types
dtypes = {
    0: 'S40',
    1: 'i2',
    2: 'f4',
    3: 'u4',
    4: 'b1',
    5: 'i4',
    6: 'f8',
    7: 'U40',
    8: 'i2',
    9: 'f4',
    10: 'u4',
    11: 'b1',
    12: 'i4',
    13: 'f8'
}

dsize = {
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

dbrtypes = {
    'STRING': 0,
    'INT': 1,
    'SHORT': 1,
    'FLOAT': 2,
    'ENUM': 3,
    'CHAR': 4,
    'LONG': 5,
    'DOUBLE': 6
}


class Chunk(object):
    def __init__(self, header):
        self.header = header
        self.events = []
        self.meta = None
        self.value = None

    def add(self, event):
        self.events.append(event)
