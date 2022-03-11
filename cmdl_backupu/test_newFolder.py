from unittest import TestCase

from cmdl_backupu.new_folder import *


class TestNewFolder(TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path.cwd()
        strDir4Test = 'TestBackupZFolder'
        pBase = p.parent.joinpath(strDir4Test)

        if not pBase.exists():
            pBase.mkdir()
        cls.base_folder = pBase
        cls.test_name = 'COPY_TEST'

    def setUp(self):
        self.base_folder = TestNewFolder.base_folder

    @classmethod
    def tearDownClass(cls):
        cls.base_folder.rmdir()
        # super().tearDownClass()

    def test_folder(self):
        new_folder = newFolder(strBaseFolder=self.base_folder,
                               sub_name='TEST', prefix='COPY')
        self.assertEqual(new_folder.folder, self.base_folder.joinpath('COPY_TEST'))

    def test__zip_folder(self):
        new_folder = newFolder(strBaseFolder=self.base_folder,
                               sub_name='TEST', prefix='COPY', archive_format='zip')
        self.assertEqual(new_folder.folder, self.base_folder.joinpath('COPY_TEST.zip'))

    def test_raise_rule(self):
        _fld = self.base_folder.joinpath('COPY_TEST')
        if not _fld.exists():
            _fld.mkdir()

        new_folder = newFolder(strBaseFolder=self.base_folder,
                               sub_name='TEST', prefix='COPY')

        try:
            f = new_folder.folder
            print(f)
            self.assertTrue(False)
        except FileExistsError:
            _fld.rmdir()
            self.assertTrue(True)

    def test_inc_rule(self):
        _fld = self.base_folder.joinpath('COPY_TEST')
        if not _fld.exists():
            _fld.mkdir()

        new_folder = newFolder(strBaseFolder=self.base_folder,
                               sub_name='TEST', prefix='COPY', exsist_rule=incRule())
        f_ex = str(_fld)
        f_new = str(new_folder.folder)
        _fld.rmdir()

        self.assertNotEqual(f_ex, f_new)

    def test_inc_zip_rule(self):
        _fld = self.base_folder.joinpath('COPY_TEST.zip')
        _fld.touch()

        new_folder = newFolder(strBaseFolder=self.base_folder, archive_format='zip',
                               sub_name='TEST', prefix='COPY', exsist_rule=incRule())
        f_ex = str(_fld)
        f_new = str(new_folder.folder)
        _fld.unlink()

        self.assertEqual(str(self.base_folder.joinpath('COPY_TEST_1.zip')), f_new)

    def test_dateinc_rule(self):
        _fld = self.base_folder.joinpath('COPY_TEST')
        if not _fld.exists():
            _fld.mkdir()

        new_folder = newFolder(strBaseFolder=self.base_folder,
                               sub_name='TEST', prefix='COPY')
        diRule = dateRuleInc(date_format='%Y_%m_%d')
        new_folder.exists_rule = diRule
        dtStr = dt.datetime.now().strftime('%Y_%m_%d')

        f_new = str(new_folder.folder)
        _fld.rmdir()

        self.assertEqual(str(self.base_folder.joinpath('COPY_TEST_{}'.format(dtStr))), f_new)

    def test_dateinc_zip_rule(self):
        _fld = self.base_folder.joinpath('COPY_TEST.zip')
        _fld.touch()

        new_folder = newFolder(strBaseFolder=self.base_folder, archive_format='zip',
                               sub_name='TEST', prefix='COPY')
        diRule = dateRuleInc(date_format='%Y_%m_%d')
        new_folder.exists_rule = diRule
        dtStr = dt.datetime.now().strftime('%Y_%m_%d')

        f_new = str(new_folder.folder)
        _fld.unlink()

        self.assertEqual(str(self.base_folder.joinpath('COPY_TEST_{}.zip'.format(dtStr))), f_new)
