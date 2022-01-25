from unittest import TestCase, main
from cmdl_backpz.scan import *
from cmdl_backpz.filters import *

class TestXScan(TestCase):
    def setUp(self):
        self.xScan = xScan()
        self.xScan.scan()

    def test_scan(self):
        """ test simple scan on current dir  """
        _lst = self.xScan.files()
        self.assertTrue(len(_lst) > 0)

    def test_scan_filter_allpath(self):
        """ test scan fith base path filters black-white  """
        start_pos = len(self.xScan.base_path)
        filters = [
            fFilePath(color=filter_color.WHITE, case=string_case.STRICT, rules=r'\.py', start_position=start_pos),
            fFilePath(color=filter_color.BLACK, case=string_case.STRICT, rules=r'\\__init__', start_position=start_pos)
        ]
        self.xScan.set_filters(*filters)
        self.assertTrue(self.xScan.size(filtered=False) > self.xScan.size(filtered=True))

