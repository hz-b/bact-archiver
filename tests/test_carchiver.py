import os
import unittest

from bact.epics.archiver.archiver2 import get_data
from bact.epics.archiver.carchiver import get_data as cget_data
from common import test_data_dir


class ArchiverClientTest(unittest.TestCase):
    """Test the decoding of PB/HTTP formated archiver data
    """

    def read(self, fname):
        fullname = os.path.join(test_data_dir, fname)
        print('reading {}'.format(fullname))
        with open(fullname,'rb') as f:
            return f.read()

    def run_decode(self,*,fname=None, **kw):
        data = self.read(fname)

        header, values = get_data(data)
        print(header)

        self.assertEqual(header.type, kw['exp_type'])
        self.assertEqual(len(values), kw['exp_len'])

        self.assertEqual(header.elementCount, kw.get('exp_count', 1))

    def test00_scalar_string(self):

        self.run_decode(fname='20171101_stGun.pb',
                        exp_type=0,
                        exp_len=5)

    def test03_scalar_enum(self):

        self.run_decode(fname='20171101_selTrgSR.pb',
                        exp_type=3,
                        exp_len=4)
        # TODO check all these nice extra info in the header ...

    def test05_scalar_long(self):
        self.run_decode(fname='20171101_numShots.pb',
                        exp_type=5,
                        exp_len=29)

    def test06_scalar_double(self):

        self.run_decode(fname='201710010200_rdCur.pb',
                        exp_type=6,
                        exp_len=56)

    def test08_vector_short(self):

        self.run_decode(fname='20171101_sram_maxrms.pb',
                        exp_type=8,
                        exp_len=121,
                        exp_count=31457)

    def test09_vector_float(self):

        self.run_decode(fname='20171101_sram_mean.pb',
                        exp_type=9,
                        exp_len=241,
                        exp_count=400)

    @unittest.skip('broken input file')
    def test11_vector_char(self):

        self.run_decode(fname='20171101_sram_mask.pb',
                        exp_type=11,
                        exp_len=121,
                        exp_count=400)

    @unittest.skip('broken input file')
    def test12_vector_int(self):

        self.run_decode(fname='20171101_fullhistogram.pb',
                        exp_type=12,
                        exp_len=121,
                        exp_count=6255)

    def test13_vector_double(self):

        self.run_decode(fname='20171101_MBcurrent.pb',
                        exp_type=13,
                        exp_len=121,
                        exp_count=400)


class CythonArchiverClientTest(ArchiverClientTest):
    """Test cython base archiver client
    """

    def run_decode(self, *, fname=None, **kw):
        data = self.read(fname)

        data = cget_data(data)
        header = data.meta['header']
        values = data.values
        print(header)

        self.assertEqual(header.type, kw['exp_type'])
        self.assertEqual(len(values), kw['exp_len'])

        self.assertEqual(header.elementCount, kw.get('exp_count', 1))


if __name__ == "__main__":
    unittest.main()
