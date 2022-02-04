"""
   make name for destination folder for save backup or cope files;
   make path for this new folder from given base path;
   if the path contains such a folder, then we try to create a new name from the original one using some rules

   classes:

    abcNewFolderExistsRule - base abstruct class for create work-with-exsist-folder rule
    errorRule - if folder exists raise exception FileExistsError
    incRule - increment rule: if folder with given name already exists, add suffix '<delimiter><number>' to base name:
            for ex. trying create folder COPY_TEST in given path, if exists - create COPY_TEST_1,
            if such exists - create COPY_TEST_2 etc. Num in suffix - max_num + 1 for such folders
    msecRule - if folder with given name already exists, add suffix '<delimiter><time in msec from epoch>' to base name:
            for ex. trying create folder COPY_TEST in given path, if exists - create COPY_TEST_1643824667561
    dateRuleInc - if folder with given name already exists, add suffix '<delimiter><current date in given format>'
            to base name, if such folder also exists try create new name using incRule for new name (given name + date):
            for ex. trying create folder COPY_TEST in given path, if exists - create COPY_TEST_COPY_TEST_2022-02-02;
            if exists - create create COPY_TEST_COPY_TEST_2022-02-02_1 etc
    dateRuleMSec - if folder with given name already exists, add suffix '<delimiter><current date in given format>'
            to base name, if such folder also exists try create new name using msecRule for new name (given name + date):
            for ex. trying create folder COPY_TEST in given path, if exists - create COPY_TEST_COPY_TEST_2022-02-02;
            if exists - create create COPY_TEST_2022-02-02_1643824667561 etc

    newFolder - main class for module, create new name for folder inside given base folder; if such folder already
            exists apply rule, passed in class, for create non-exists folder name
"""

# TODO: make check on valid chars in new path

import datetime as dt
import re
from abc import ABC, abstractmethod
from pathlib import Path


class abcNewFolderExistsRule(ABC):
    """
    base class for resolve new-folder-already-exists situation. New folder name construct from given by append to it
    some unique suffix. If given name is archive file names - create new file name by add suffix to name, not extension
    for create new name class has needed base name, parent folder name, archive extension and delimiter string from
    upper class
    """

    @property
    def base_path(self):
        return self._base_path

    @property
    def base_name(self):
        return self._base_name

    @property
    def delimiter(self):
        return self._delimiter

    def archive(self, is_re=False):
        if self._archive:
            _ret = '\\.{}' if is_re else '.{}'
            return _ret.format(self._archive)
        else:
            return ''

    def sub_init(self, base_path='', base_name='', delimiter='', archive=''):
        """
        sub-constructor for init class object after create upper class object
        :param base_path:
        :param base_name:
        :param delimiter:
        :param archive:
        :return:
        """
        self._base_path = base_path
        self._base_name = base_name
        self._delimiter = delimiter
        self._archive = archive

    @abstractmethod
    def new_path(self):
        """
        create new folder name
        :return: path - new, unique for base path, folder name
        """
        pass


class errorRule(abcNewFolderExistsRule):
    def new_path(self):
        raise FileExistsError


class exsistOKRule(abcNewFolderExistsRule):
    def new_path(self):
        # new_name = '{name}'.format(name=self.base_name, dl=self.delimiter, num=next_num)
        new_name = self.base_name + self.archive()
        new_path = self.base_path.joinpath(new_name)
        return new_path


class incRule(abcNewFolderExistsRule):
    @property
    def _search_pattern(self):
        strPat = '{subname}{dl}(?P<num>\d+)'.format(subname=self.base_name, dl=self.delimiter)
        strPat += self.archive(is_re=True)
        strPat += '$'
        return strPat

    def new_path(self):
        lst = list(self.base_path.glob('*'))
        lst_num = list()

        for l in lst:
            try:
                lst_num.append(int(re.search(self._search_pattern, l.name).group('num')))
            except AttributeError:
                pass
        try:
            next_num = max(lst_num) + 1
        except ValueError:
            next_num = 1

        new_name = '{name}{dl}{num}'.format(name=self.base_name, dl=self.delimiter, num=next_num)
        new_name += self.archive()
        new_path = self.base_path.joinpath(new_name)
        if new_path.exists():
            raise FileExistsError(new_path)

        return new_path


class msecRule(abcNewFolderExistsRule):
    @property
    def _search_pattern(self):
        strPat = '{subname}{dl}(?P<num>\d+)'.format(subname=self.base_name, dl=self.delimiter)
        strPat += self.archive(is_re=True)
        strPat += '$'
        return strPat

    def new_path(self):
        dtx = dt.datetime.now()
        ep = dt.datetime(1970, 1, 1, 0, 0, 0)
        msec_epo = int((dtx - ep).total_seconds() * 1e3)

        new_name = '{name}{dl}{num}'.format(name=self.base_name, dl=self.delimiter, num=msec_epo)
        new_name += self.archive()
        new_path = self.base_path.joinpath(new_name)
        if new_path.exists():
            raise FileExistsError(new_path)

        return new_path

class dateRuleInc(incRule):
    def __init__(self, date_format='%Y-%m-%d') -> None:
        self._format = date_format

    def new_path(self):
        new_name_x = '{name}{dl}{date}'.format(name=self.base_name, dl=self.delimiter,
                                               date=dt.datetime.now().strftime(self._format))
        new_name = new_name_x + self.archive()

        new_path = self.base_path.joinpath(new_name)
        if new_path.exists():
            old_name = self.base_name
            self._base_name = new_name_x
            new_name = super().new_path()
            self._base_name = old_name
            return self.base_path.joinpath(new_name)
        else:
            return new_path

class dateRuleMSec(msecRule):
    # def __init__(self, date_format='%Y-%m-%d') -> None:
    #     self._format = date_format
    #
    # def new_path(self):
    #     new_name_x = '{name}{dl}{date}'.format(name=self.base_name, dl=self.delimiter,
    #                                            date=dt.datetime.now().strftime(self._format))
    #     new_name = new_name_x + self.archive()
    #
    #     new_path = self.base_path.joinpath(new_name)
    #     if new_path.exists():
    #         old_name = self.base_name
    #         self._base_name = new_name_x
    #         new_name = super().new_path()
    #         self._base_name = old_name
    #         return self.base_path.joinpath(new_name)
    #     else:
    #         return new_path

    def __init__(self, date_format='%Y-%m-%d') -> None:
        self._format = date_format

    def sub_init(self, base_path='', base_name='', delimiter='', archive=''):
        super().sub_init(base_path, base_name, delimiter, archive)
        self._path_created = self._create_new_path()

    def _create_new_path(self):
        new_name_x = '{name}{dl}{date}'.format(name=self.base_name, dl=self.delimiter,
                                               date=dt.datetime.now().strftime(self._format))
        new_name = new_name_x + self.archive()

        _new_path = self.base_path.joinpath(new_name)
        if _new_path.exists():
            old_name = self.base_name
            self._base_name = new_name_x
            new_name = super().new_path()
            self._base_name = old_name
            return self.base_path.joinpath(new_name)
        else:
            return _new_path

    def new_path(self):
        return self._path_created


class newFolder:
    """
    create new, non-exists folder name inside given base folder. If new folder already exists try to resolve new name
    applying exists_rule, pass in params (exsist_rule)
    public properties:
        base_path - return given base path for parent folder
        folder - retrun path to new? working, folder
        exists_rule - return or set exists_rule object, instance of abcNewFolderExistsRule class (must be setted
        before call folder property - or exists_rule must be passed in constructor)
    """

    def __init__(self, strBaseFolder: [type(None), str, Path] = None,
                 prefix: str = '', sub_name: str = '', delimiter: str = '_', archive_format: str = '',
                 exsist_rule: abcNewFolderExistsRule = errorRule()) -> None:
        """

        :param strBaseFolder: path or pathlike string for parent folder
        :param prefix: str - prefix for new folder name
        :param sub_name: str - new folder name
        :param delimiter: str - delimiter for prefix (if given) and suffix (if folder with such name already exists in base path)
        :param archive_format: str - extension that define archive format for copy or backup file in archive file instead of destionation folder
        :param exsist_rule: abcNewFolderExistsRule - class for resolve name for existing folder
        """
        assert Path(strBaseFolder).exists()
        assert Path(strBaseFolder).is_dir()

        self._basePath = Path(strBaseFolder)

        self._prefix = prefix
        self._sub_name = sub_name
        self._delimiter = delimiter
        self._work_path = ''
        self._archive = archive_format

        self._exists_rule = exsist_rule
        self._exists_rule.sub_init(base_path=self.base_path, base_name=self._base_name, delimiter=self._delimiter,
                                   archive=self._archive)

    @property
    def prefix(self):
        return self._prefix

    @property
    def delimiter(self):
        return self._delimiter

    @property
    def subname(self):
        return self._sub_name

    @property
    def exists_rule(self):
        """
        :return: object for resolve exist folder
        """
        return self._exists_rule

    @exists_rule.setter
    def exists_rule(self, value):
        assert isinstance(value, abcNewFolderExistsRule)
        self._exists_rule = value
        self._exists_rule.sub_init(base_path=self.base_path, base_name=self._base_name, delimiter=self._delimiter,
                                   archive=self._archive)

    @property
    def _base_name(self):
        """
        :return: str - construct base new folder name from prefix, delimiter and sub_name
        """
        _dp = self._delimiter if self._prefix else ''
        base_name = '{prefix}{dp}{sub_name}'.format(prefix=self._prefix, dp=_dp, sub_name=self._sub_name)
        return base_name

    @property
    def _archive_name(self):
        """
        :return: str - add archive extension for folder name - make it file name, for working archive file
        """
        if self._archive:
            return '.{}'.format(self._archive)
        else:
            return ''

    def _construct_subpath(self):
        """
        :return: path - construct path for new folder, check folder exists, apply rule for resolve folder -exists situation
        """
        sub_path = self._base_name + self._archive_name
        work_path = self.base_path.joinpath(sub_path)

        if not work_path.exists():
            return work_path
        else:
            # path exist - make new from path increment rule
            return self._exists_rule.new_path()

    @property
    def folder(self):
        """
        :return: path - path to new checked working folder. Folder is not created - only name
        """
        return self._construct_subpath()

    @property
    def base_path(self):
        """
        :return: path - base or parent folder
        """
        return self._basePath


class _testNewFolder:
    """class for testing main working classes """

    def __init__(self):
        p = Path.cwd()
        # create 'TestFolder' in current dir, inside it will be some test files and dirs
        strDir4Test = 'TestFolder'
        pBase = p.parent.joinpath(strDir4Test)
        if not pBase.exists():
            pBase.mkdir()
        self._basepath = pBase

        self._dtformat = '%Y_%m_%d'

        # create test dirs
        self._td = [self._basepath.joinpath('COPY_TEST'), self._basepath.joinpath('COPY_TEST_1'),
                    self._basepath.joinpath('COPY_TEST_4'),
                    self._basepath.joinpath('COPY_TEST_{dt}'.format(dt=dt.datetime.now().strftime(self._dtformat))),
                    self._basepath.joinpath('COPY_TEST_{dt}_1'.format(dt=dt.datetime.now().strftime(self._dtformat)))]

        # create test zip-files
        self._tf = [self._basepath.joinpath('COPY_TEST.zip'), self._basepath.joinpath('COPY_TEST_1.zip'),
                    self._basepath.joinpath('COPY_TEST_6.zip'),
                    self._basepath.joinpath('COPY_TEST_{dt}.zip'.format(dt=dt.datetime.now().strftime(self._dtformat))),
                    self._basepath.joinpath(
                        'COPY_TEST_{dt}_10.zip'.format(dt=dt.datetime.now().strftime(self._dtformat)))]

        # fZip = self.base_folder.joinpath('COPY_TEST.zip')
        # fZip.touch()

        # for d in self._td:
        #     print(d)
        #
        # for f in self._tf:
        #     print(f)

    def test_new_folder(self):
        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY')
        return fld.folder

    def test_new_zip(self):
        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY', archive_format='zip')
        return fld.folder

    def test_new_folder_error(self):
        if not self._td[0].exists():
            self._td[0].mkdir()
        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY')
        try:
            f = fld.folder
        except FileExistsError:
            self._td[0].rmdir()
            return str(self._td[0]) + ' already ezists'

    def test_new_zip_error(self):

        self._tf[0].touch()
        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY', archive_format='zip')
        try:
            f = fld.folder
        except FileExistsError:
            self._tf[0].unlink()
            return str(self._tf[0]) + ' already ezists'

    def test_new_folder_inc(self):
        for d in self._td:
            d.mkdir()

        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY', exsist_rule=incRule())
        f = fld.folder

        for d in self._td:
            d.rmdir()
        return f

    def test_new_zip_inc(self):
        for f in self._tf:
            f.touch()

        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST',
                        prefix='COPY', archive_format='zip', exsist_rule=incRule())
        fff = fld.folder

        for f in self._tf:
            f.unlink()

        return fff

    def test_new_folder_incdate(self):
        for d in self._td:
            d.mkdir()

        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY',
                        exsist_rule=dateRuleInc(date_format=self._dtformat))
        f = fld.folder

        for d in self._td:
            d.rmdir()
        return f

    def test_new_zip_incdate(self):
        for d in self._tf:
            d.touch()

        fld = newFolder(strBaseFolder=str(self._basepath), sub_name='TEST', prefix='COPY',
                        exsist_rule=dateRuleInc(date_format=self._dtformat), archive_format='zip')
        f = fld.folder

        for d in self._tf:
            d.unlink()
        return f

    def __delete__(self, instance):
        self._basepath.rmdir()


def check_folder_class():
    tt = _testNewFolder()
    print(tt.test_new_folder())
    print(tt.test_new_zip())
    print(tt.test_new_folder_error())
    print(tt.test_new_zip_error())
    print(tt.test_new_folder_inc())
    print(tt.test_new_zip_inc())
    print(tt.test_new_folder_incdate())
    print(tt.test_new_zip_incdate())

    # p = Path.cwd()
    # strDir4Test = 'TestFolder'
    # pBase = p.parent.joinpath(strDir4Test)
    #
    # if not pBase.exists():
    #     pBase.mkdir()
    #
    # fld = newFolder(strBaseFolder=str(pBase), sub_name='TEST', prefix='COPY', exsist_rule=msecRule())#, archive_format='zip')
    # x=dateRuleMSec()
    # fld.exists_rule = x
    # print('base', fld.base_path)
    # print('new',  fld.folder)



if __name__ == '__main__':
    check_folder_class()

    print('All done.')
