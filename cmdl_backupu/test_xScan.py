from unittest import TestCase

from cmdl_backupu.actions import set_archive_sttrib
from cmdl_backupu.scan import *


class TestXScan(TestCase):
    @classmethod
    def setUpClass(cls):
        print('set up class')
        cls.xScan = xScan()
        cls.xScan.scan()

    def setup(self):
        self.xScan = TestXScan.xScan
        # self.xScan.scan()

        # def setUp(self):

        # self.xScan = xScan()
        # self.xScan.scan()

    def test_scan(self):
        """ test simple scan on current dir  """
        _lst = self.xScan.files()
        self.assertTrue(len(_lst) > 0)

    def test_scan_filter_allpath(self):
        """ test scan file base path filters black-white  """

        filters = [
            filterFilePath(color=filter_color.WHITE, case=string_case.STRICT, rule=r'\.py\b'),
            filterFilePath(color=filter_color.BLACK, case=string_case.STRICT, rule=r'__init__')
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

    def test_scan_filter_dir(self):
        """ test scan file parent dirs filters black-white  """

        filters = [
            filterDirName(color=filter_color.WHITE, case=string_case.STRICT, rule=r'__pycache__'),
            filterDirName(color=filter_color.BLACK, case=string_case.STRICT, rule=r'__pycache__')]

        self.xScan.set_filters(*filters)
        self.assertTrue(self.xScan.size(filtered=True) == 0)

    def test_scan_filter_size(self):
        """ test scan file parent dirs filters black-white  """

        filters = [
            filterFileSize(color=filter_color.WHITE, low_level=10, high_level=5e3),
            filterFileSize(color=filter_color.BLACK, low_level=50)
        ]

        self.xScan.set_filters(*filters)
        self.assertTrue(self.xScan.size(filtered=True) == 1)

    def test_scan_filter_arch_attrib(self):
        """ test scan file a-attrib filters black-white  """
        if platform.system() == 'Windows':
            dn = filterFileName(color=filter_color.WHITE, case=string_case.STRICT, rule=r'__init__')

            self.xScan.scan()
            self.xScan.set_filters(dn)
            for f in self.xScan.files(filtered=True):
                set_archive_sttrib(f['path'], AAtrib_ON=False)

            fAAtrW = filterArchAttrib(color=filter_color.WHITE)
            fAAtrB = filterArchAttrib(color=filter_color.BLACK)

            self.xScan.scan()
            self.xScan.set_filters(fAAtrB)
            self.assertTrue(self.xScan.size(filtered=True) >= 1)
        else:
            self.assertTrue(True)

    def test_scan_filter_changedate_range(self):
        """ test scan file date change filters black-white  """

        self.xScan.scan()

        dt_filter = self.xScan.files(filtered=False)[2]['change_date']
        delta = dt.timedelta(days=366)

        fDtRangeW = filterFileDateRange(color=filter_color.WHITE,
                                        low_date=dt_filter,
                                        high_date=dt_filter + delta)
        fDtRangeB = filterFileDateRange(color=filter_color.BLACK,
                                        high_date=dt_filter - dt.timedelta(days=1))

        self.xScan.set_filters(fDtRangeW)
        bW = self.xScan.size(filtered=True) >= 1

        self.xScan.set_filters(fDtRangeB)
        bB = self.xScan.size(filtered=True) >= 1

        self.assertTrue(bW and bB)

    def test_scan_filter_changedate_exact(self):
        """ test scan file date change filters black-white  """

        self.xScan.scan()

        fDtRangeW = filterFileDateExact(color=filter_color.WHITE,
                                        file_date=dt.date(day=14, month=1, year=2022))
        fDtRangeB = filterFileDateExact(color=filter_color.BLACK,
                                        file_date=dt.date(day=14, month=1, year=2022))

        self.xScan.set_filters(fDtRangeW)
        bW = self.xScan.size(filtered=True) >= 1

        self.xScan.set_filters(fDtRangeB)
        bB = self.xScan.size(filtered=True) != 0  # file __init__.py changed 2020-01-28

        self.assertTrue(bW and bB)
