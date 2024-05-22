# -*- coding: utf-8 -*-
# -*- python -*-
# cython: language_level = 3str
# distutils: language = c++
# Author: Andreas Schälicke <andreas.schaelike@helmholtz-berlin.de>
# Date: 2017
"""Handling of EPICS archiver data

Documentation of the Archiver Protocol-buffer format:
    * https://slacmshankar.github.io/epicsarchiver_docs/pb_pbraw.html
    * https://developers.google.com/protocol-buffers/docs/cpptutorial


The following functions are expected to be called by external modules?
    * :func:`read_chunk`
    * :func:`read_header`
"""

# read EPICSEvent.pxd definition of Protocol-Buffer code
from proto.epics_event cimport PayloadInfo,  string
from proto.epics_event cimport ScalarDouble, ScalarString, ScalarEnum, ScalarInt
from proto.epics_event cimport VectorDouble, VectorFloat
from proto.epics_event cimport VectorInt, VectorShort, VectorChar

import numpy as np
cimport numpy as np
cimport cython



@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
cdef string cdecode(const char[:] data, string & res) noexcept nogil:
    """Decode a PB message.

    Args:
        data : a char buffer

    Returns:
        string : a reference to the string to place the result into

    As serialized PB messages are binary data; after serialization, newline
    characters are escaped to maintain a "sample per line" constraint.

    ASCII codes are escaped in the following manner:
    * ``0x1B`` to  ``0x1B 0x01``
    * newline character ``\n`` =  ``0x0A`` to ``0x1B 0x02``
    * carriage return character ``0x0D`` to  ``0x1B 0x03``


    This encoding is reversed here

    WARNING:
           This function does not check that the string res is long enough!
    """
    cdef string *res_p = & res
    res_p.clear()
    cdef char c
    cdef int i=0
    cdef int N = data.shape[0]
    while i<N:
        c = data[i]
        if c==b'\x1b':
            i+=1
            c = data[i]
            if c==b'\x02':
                res_p[0]+=<char>b'\x0a'
            elif c==b'\x03':
                res_p[0]+=<char>b'\x0d'
            elif c==b'\x01':
                res_p[0]+=<char>b'\x1b'
        else:
            res_p[0]+=c
        i+=1

    return res


@cython.boundscheck(False)
@cython.wraparound(False)
cdef int count_lines(char[:] seq) nogil:
    """Number of new lines in the whole seq

    Args:
        seq: a character sequence

    Returns:
        count: position of new line

    New lines are defined by '\n'
    """
    cdef int N = seq.shape[0]
    cdef int i
    if N==0 :
        return 0
    cdef int count = 1
    for i in range(N):
        if seq[i] == '\n':
            count+=1
    return count

@cython.boundscheck(False)
@cython.wraparound(False)
cdef int cnext(char[:] seq, int idx) nogil:
    """find end of current line
    """
    cdef int N = seq.shape[0]
    cdef int i
    for i in range(idx,N):
        if seq[i] == '\n':
            return i
    return N

# reads one "chunk" according to the PB/HTTP protocol
# using defined "decoder" for the given EPICS type
# returning three numpy arrays

#
# ---------- SCALAR EPICS TYPES --------------------
#

# -0- EPICS STRING
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_chunk_str(char[:] seq, int N, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):

    values = np.empty(N,dtype=object)

    cdef ScalarString event

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf

    # needs GIL
    for i in range(N):
        start = stop+1
        stop = cnext(seq, start)
        event.ParseFromString(cdecode(seq[start:stop],buf))
        values[i] = event.val()
        secs[i] = event.secondsintoyear()
        nanos[i] = event.nano()

    return values,secs,nanos

# -3- EPICS ENUM
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_chunk_enum(char[:] seq, int N, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.int32_t] values = np.empty(N,dtype=np.int32)

    cdef ScalarEnum event

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            values[i] = event.val()
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()

    return values,secs,nanos

# -5- EPICS LONG
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_chunk_i4(char[:] seq, int N, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.int32_t] values = np.empty(N,dtype=np.int32)

    cdef ScalarInt event

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            values[i] = event.val()
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()

    return values,secs,nanos

# -6- EPICS DOUBLE - tested
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_chunk_f8(char[:] seq, int N, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.float_t] values = np.empty(N,dtype=np.float)

    cdef ScalarDouble event

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            values[i] = event.val()
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()

    return values,secs,nanos


#
# ---------- WAVEFORM EPICS TYPES --------------------
#

# -8- WAVEFORM SHORT - tested
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_vchunk_i2(char[:] seq, int N, int elements, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.int16_t, ndim=2] values = np.empty((N,elements),dtype=np.int16)

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf

    cdef VectorShort event
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            for j in range(elements):
                values[i,j] = event.val(j)
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()
    return values, secs, nanos


# -12- WAVEFORM LONG - failed?!
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_vchunk_i4(char[:] seq, int N, int elements, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.int32_t, ndim=2] values = np.empty((N,elements),dtype=np.int32)

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf

    cdef VectorInt event
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            for j in range(elements):
                values[i,j] = event.val(j)
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()
    return values, secs, nanos

# -9- WAVEFORM FLOAT - tested
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_vchunk_f4(char[:] seq, int N, int elements, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.float32_t, ndim=2] values = np.empty((N,elements),dtype=np.float32)

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf

    cdef VectorFloat event
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            for j in range(elements):
                values[i,j] = event.val(j)
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()
    return values, secs, nanos

# -13- WAVEFORM DOUBLE - tested
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_vchunk_f8(char[:] seq, int N, int elements, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.float64_t, ndim=2] values = np.empty((N,elements),dtype=np.float64)

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf

    cdef VectorDouble event
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            for j in range(elements):
                values[i,j] = event.val(j)
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()
    return values, secs, nanos

# -11- WAVEFORM CHAR
@cython.boundscheck(False)
@cython.wraparound(False)
cdef read_vchunk_char(char[:] seq, int N, int elements, np.ndarray[np.int32_t] secs, np.ndarray[np.int32_t] nanos):
    cdef np.ndarray[np.int8_t, ndim=2] values = np.empty((N,elements),dtype=np.int8)

    cdef int i
    cdef int start = 0
    cdef int stop = -1
    cdef string buf, val

    cdef VectorChar event
    with nogil:
        # should be save to release GIL here
        for i in range(N):
            start = stop+1
            stop = cnext(seq, start)
            event.ParseFromString(cdecode(seq[start:stop],buf))
            val = event.val()
            for j in range(elements):
                values[i,j] = val[j]
            secs[i] = event.secondsintoyear()
            nanos[i] = event.nano()
    return values, secs, nanos


#
# ---- PYTHON functions ----
#
def read_chunk(char[:] seq, header):
    """Read a protocol buffer chunk

    Args:
        seq : a character buffer
        epics_type : an integer defining the epics type
        elements   : the number of elements


    Returns:
      values, seconds, nano_seconds


    Currently the following epics types are implemented:
        *  0.  : string
        *  3.  : enum
        *  5.  : i4 (signed integers of four bytes)
        *  6.  : f8 (doubles of eight bytes)
        *  9.  : i2 vector (signed [short] integers of two bytes)
        *  11. : vector of characters
        *  12. : f4 vector (floats of four bytes)
        *  13. : f8 vector (floats of eight bytes)

    """
    cdef int epics_type = header.type
    cdef int elements = header.elementCount
    cdef int N = count_lines(seq)

    cdef np.ndarray[np.int32_t] secs = np.empty(N,dtype=np.int32)
    cdef np.ndarray[np.int32_t] nanos = np.empty(N,dtype=np.int32)

    if epics_type==0:
        return read_chunk_str(seq, N, secs, nanos)
    elif epics_type==3:
        return read_chunk_enum(seq, N, secs, nanos)
    elif epics_type==5:
        return read_chunk_i4(seq, N, secs, nanos)
    elif epics_type==6:
        return read_chunk_f8(seq, N, secs, nanos)
    elif epics_type==8:
        return read_vchunk_i2(seq, N, elements, secs, nanos)
    elif epics_type==9:
        return read_vchunk_f4(seq, N, elements, secs, nanos)
    elif epics_type==11:
        return read_vchunk_char(seq, N, elements, secs, nanos)
    elif epics_type==12:
        return read_vchunk_i4(seq, N, elements, secs, nanos)
    elif epics_type==13:
        return read_vchunk_f8(seq, N, elements, secs, nanos)

    # Why not raise an exception here
    raise NotImplementedError('Type {} not supported'.format(epics_type))


def decode(char[:] line):
    """Simple python wraper for cdecode
    """
    cdef string buf
    cdecode(line,buf)
    return buf

def read_header(char[:] line):
    """Read the header of the payload

    Args:
        line : char buffer

    Returns:
        dic: dictionary containing
            * type
            * year
            * elementcount

    use carchiver.read_header if PayloadInfo is need directly
    """
    cdef PayloadInfo info = PayloadInfo()
    cdef string buf
    info.ParseFromString(cdecode(line,buf))

    header = {}
    header['type'] = info.type()
    header['year'] = info.year()
    header['elementcount'] = info.elementcount()

    return header
