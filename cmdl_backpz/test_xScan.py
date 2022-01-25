from unittest import TestCase, main
from cmdl_backpz.scan import *

class TestXScan(TestCase):
    def setUp(self):
        self.xScan = xScan()

    def test_scan(self):
        """ test simple scan on current dir  """
        self.xScan.scan()
        _lst = self.xScan.files()
        self.assertTrue(len(_lst) > 0)

if __name__ == '__main__':
    # main()
    sc = xScan()
    print(sc.scan() )