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
        """ test scan file base path filters black-white  """

        filters = [
            filterFilePath(color=filter_color.WHITE, case=string_case.STRICT, rule=r'\.py'),
            filterFilePath(color=filter_color.BLACK, case=string_case.STRICT, rule=r'\\__init__')
        ]
        self.xScan.set_filters(*filters)
        self.assertTrue(
            (self.xScan.size(filtered=False) > self.xScan.size(filtered=True)) and
            (self.xScan.size(filtered=True) > 0))

    def test_scan_filter_filename(self):
        """ test scan file name filters black-white  """

        filters = [
            filterFileName(color=filter_color.WHITE, case=string_case.STRICT, rule=r'_'),
            filterFileName(color=filter_color.BLACK, case=string_case.STRICT, rule=r'test')
        ]
        self.xScan.set_filters(*filters)
        self.assertTrue(
            (self.xScan.size(filtered=False) > self.xScan.size(filtered=True)) and
            (self.xScan.size(filtered=True) > 0))

    def test_scan_filter_fileext(self):
        """ test scan file name filters black-white  """

        filters = [
            filterFileExt(color=filter_color.WHITE, case=string_case.STRICT, rule=r'py.*'),
            filterFileExt(color=filter_color.BLACK, case=string_case.STRICT, rule=r'pyc')]

        self.xScan.set_filters(*filters)
        self.assertTrue(self.xScan.size(filtered=True) > 0)
