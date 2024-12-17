# distutils: language = c++
# cython: language_level = 2


from libcpp.string cimport string
from libcpp cimport bool

cdef extern from "google/protobuf/stubs/port.h" namespace "::google::protobuf":
     ctypedef int int32
     ctypedef int uint32

cdef extern from "epics_event.pb.h" namespace "EPICS":
    cdef enum PayloadType:
        pass

    cdef cppclass FieldValue:
        pass

    cdef cppclass PayloadInfo nogil:
        PayloadInfo() except +
        bool ParseFromString(const string& data) except +
        int32 year()
        PayloadType type()
        int32 elementcount()
        string pvname()
        int32 headers_size()
        FieldValue headers(int)

    # LINAC1C:stGun
    cdef cppclass ScalarString nogil:
        ScalarString() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        string val()

    # TOPUPCC:rdCur
    cdef cppclass ScalarDouble nogil:
        ScalarDouble() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        float val()

    # TOPUPCC:numShots
    cdef cppclass ScalarInt nogil:
        ScalarInt() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        int32 val()

    # TOPUPCC:selTrgSR
    cdef cppclass ScalarEnum nogil:
        ScalarEnum() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        int32 val()

    # CUMZR:MBcurrent
    cdef cppclass VectorDouble nogil:
        VectorDouble() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        float val(int)

    # BBQR:X:SRAM:MEAN
    cdef cppclass VectorFloat nogil:
        VectorFloat() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        float val(int)

    # BBQR:X:FB:MASK
    cdef cppclass VectorChar nogil:
        VectorChar() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        string val()

    # BBQR:X:SRAM:MAXRMS
    cdef cppclass VectorShort nogil:
        VectorShort() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        int32 val(int)

    # FILL:fullhistogram
    cdef cppclass VectorInt nogil:
        VectorInt() except +
        bool ParseFromString(const string& data) except +
        uint32 secondsintoyear()
        uint32 nano()
        int32 val(int)
