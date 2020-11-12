from bact_archiver.carchiver import archiver
from bact_archiver.archiver2 import archiver
from bact_archiver.archiver2 import set_archiver_url #, convert_datetime_to_timestamp
import numpy as np
import unittest
import datetime
import logging

logger = logging.getLogger('bact')
# logger.setLevel(logging.DEBUG)


class CArchiverTest(unittest.TestCase):
    '''Access to scalar and vector / waveform data
    '''

    def setUp(self):
        # set_archiver_url('AAPL')
        # set_archiver_url("FASTZC")
        set_archiver_url("FASTZC proxy")
        # t0 = datetime.datetime(2020, 1, 8, 0, 31, 2, 237000)
        # t1 = datetime.datetime(2020, 1, 8, 0, 34, 41, 837000)
        # t0 = convert_datetime_to_timestamp(t0)
        # t1 = convert_datetime_to_timestamp(t1)

        # Data is accessed from fast archiver
        # This data is gone after 2 weeks. needs to be fixed that these
        # timestamps are automatically chosen appropriately
        t0 = '2020-03-19T18:31:02.000000Z'
        t1 = '2020-03-19T18:34:41.000000Z'

        self.start_stamp = t0
        self.end_stamp = t1

    def test00_ScalarData(self):
        '''Test reading scalar data

        Here exemplifed using the count variable of the BPM IOC
        '''
        df = archiver('MDIZ2T5G:count', t0=self.start_stamp, t1=self.end_stamp)
        df = np.array(df)
        print(df)
        l = df.shape[0]
        self.assertEqual(l, 111)

    def test02_VectorData_BPM(self):
        '''Test reading vector/waveform data using bpm data
        '''
        df = archiver('MDIZ2T5G:bdata', t0=self.start_stamp, t1=self.end_stamp)
        l0 = df.shape[0]
        self.assertEqual(l0, 111)

    def test03_VectorData_Tune(self):
        '''Test reading vector/waveform data using tune data
        '''
        df = archiver('TUNEZR:wxH', t0=self.start_stamp, t1=self.end_stamp)
        l0 = df.shape[0]
        self.assertEqual(l0, 111)


if __name__ == "__main__":
    unittest.main()
