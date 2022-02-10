import logging
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from cmdl_backpz.actions import xCopyZ
from cmdl_backpz.filters import *
from cmdl_backpz.new_folder import *
from cmdl_backpz.source_side_actions import xInfoZ


class TestXCopyZ(TestCase):
    @classmethod
    def setUpClass(cls):
        dst_base = Path.cwd()

        strDir4Test = 'TestCopy'
        pBase = dst_base.parent.joinpath(strDir4Test)

        if not pBase.exists():
            pBase.mkdir()
        cls.base_folder = pBase
        cls.test_name = 'COPY_TEST'

    @classmethod
    def tearDownClass(cls):
        rmtree(str(cls.base_folder))
        # super().tearDownClass()

    def test_run(self):
        filters = [filterFileExt(color=filter_color.WHITE, rule=r'txt'),
                   filterFileExt(color=filter_color.WHITE, rule=r'py'),
                   filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
                   filterFileExt(color=filter_color.BLACK, rule=r'ipynb'),
                   filterFileName(color=filter_color.BLACK, rule=r'TEST', case=string_case.ANY)]

        sub_name = 'TEST'
        pre_name = 'COPY'

        cw = xCopyZ(source_base_dir=str(Path('..')), log_level=logging.INFO, prefix=pre_name,
                    destination_base_dir=self.base_folder, destination_subdir=sub_name,
                    scan_filters=filters, new_folder_rule=incRule())

        cw.run()
        cw.close_log()

        xi = xInfoZ(source_base_dir=str(cw.destination_base), log_level=logging.ERROR, scan_filters=[])
        files = xi.run()
        self.assertTrue(len(files) > 0)

    def test_ziprun(self):
        filters = [filterFileExt(color=filter_color.WHITE, rule=r'txt'),
                   filterFileExt(color=filter_color.WHITE, rule=r'py'),
                   filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
                   filterFileExt(color=filter_color.BLACK, rule=r'ipynb'),
                   filterFileName(color=filter_color.BLACK, rule=r'TEST', case=string_case.ANY)]

        sub_name = 'TEST'
        pre_name = 'COPY'

        cw = xCopyZ(source_base_dir=str(Path('..')), log_level=logging.INFO, prefix=pre_name,
                    destination_base_dir=self.base_folder, destination_subdir=sub_name,
                    scan_filters=filters, new_folder_rule=incRule(), archive_format='zip')

        cw.run()
        cw.close_log()

        xi = xInfoZ(source_base_dir=str(cw.destination_base), log_level=logging.ERROR,
                    scan_filters=[filterFileExt(color=filter_color.WHITE, rule=r'zip')])
        files = xi.run()
        self.assertTrue(len(files) > 0)
