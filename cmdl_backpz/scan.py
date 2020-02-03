"""
The module contains classes for scanning the selected operating system directory (including shared network) and filters for scanned files
Files are scanned into a list with full names (including paths)
Filters inherit from an abstract class.
The module has 4 main filters
"""
import os
import subprocess
import datetime as dt
import re

from abc import ABC, abstractmethod

class FFilter(ABC):
    """ABS class - parena for file-list filters.
    Filters are black or white - black means 'not any from...', white - 'only from ...' """
    name=''
    is_on=True

    @abstractmethod
    def check(self, strPath):
        pass

    @property
    @abstractmethod
    def params(self):
        pass

    @property
    @abstractmethod
    def black(self):
        pass

    @classmethod
    def clear_list(cls, lst):
        return list(map(lambda x: x.replace('.', '').lower(), lst))

    def __str__(self):
        return '{name} - {black}\t({switch}):\t{params}'.format(name=self.name,
                                                            black='black' if self.black else 'white', params=self.params,
                                                            switch='ON' if self.is_on else 'OFF')

class x_extension_list(FFilter):
    """file extensiona filter - check files extension; may be black or white
    black - return files with no given extenstions, white - return files with only goven extensions
    black or white set in constructor
    extensions in filter-list or not used mask - only full extension"""
    _lst=list()
    _black=None

    def __init__(self, name='', lst_ext=[], black=True):
        self.name=name
        self._lst=self.clear_list(lst_ext)
        self._black=bool(black)

    def check(self, strPath):
        if self.is_on:
            return os.path.splitext(strPath)[1].replace('.', '').lower() in self._lst

    @property
    def params(self):
        return self._lst

    @property
    def black(self):
        return self._black

class x_folders(FFilter):
    """file folders filter - check files paths; may be black or white
    black - return files with not any part of path exists in filter-list,
    white - return files with any part of path having member of filter-list
    black or white set in constructor"""
    _lst=list()

    def __init__(self, name='', lst_folders=list(), black=True):
        self.name = name
        self._is_black = black
        self._lst=lst_folders.copy()

    def check(self, strPath):
        return any([re.search(p, os.path.split(strPath)[0]) for p in self._lst])

    @property
    def black(self):
        return self._is_black

    @property
    def params(self):
        return self._lst

class x_names(FFilter):
    """file name filter - check files name; may be black or white
    black - return files with names not exists in filter-list,
    white - return files with names oexists in filter-list
    black or white set in constructor"""
    _lst=list()
    _is_black=True

    def __init__(self, name='', lst_names=[], black=True):
        self.name = name
        self._is_black=black
        self._lst=lst_names.copy()

    @property
    def black(self):
        return self._is_black

    @property
    def params(self):
        return self._lst

    def check(self, strPath):
        return any([re.search(p, os.path.split(strPath)[1]) for p in self._lst])

class x_archive(FFilter):
    """file archive-attribut filter; always white;
    return files with archive-attribut is setting-up"""
    def __init__(self, name='archive'):
        self.name = name

    def check(self, strPath):
        xr = subprocess.check_output(['attrib', strPath])
        try:
            return chr(xr[0]) == 'A'
        except IndexError:
            return False

    @property
    def black(self):
        return False

    @property
    def params(self):
        return 'A-attrib of file'


class x_ge_change_date(FFilter):
    _diff_dt=None

    def __init__(self, name='', days_num=0, black=True):
        self.name=name
        self._black=bool(black)
        self._diff_dt=dt.timedelta(days=days_num)

    @property
    def params(self):
        return self._diff_dt.days

    @property
    def black(self):
        return self._black

    def check(self, strPath):
        if self.is_on:
            try:
                res=os.stat(strPath)
                mod_date=dt.datetime.fromtimestamp(res.st_mtime)
                #print(mod_date.strftime('%d.%m.%Y'), (dt.datetime.now()-self._diff_dt).strftime('%d.%m.%Y'), self._diff_dt)
                return mod_date >= (dt.datetime.now()-self._diff_dt)
            except FileNotFoundError:
                return False

#=======================================================================================================================
class FileList():
    """main class of thismodule
    scanning given folder with all sub-folders
    return filtered or un-filtered list of full files path,
    files_info re-scanning filtered or unfiltered file-list for file-info, added to full path, used for making pandas dataframe from it
    it can be swithing some filters on-off by filter name"""
    _lst_files=list()
    _strPath=''
    _filters=dict()

    def __init__(self, strBasePath):
        self._strPath=strBasePath

    def scan(self):
        lstd = [[os.path.join(i[0], f) for f in i[2]] for i in os.walk(self._strPath)]
        self._lst_files = [item for sublist in lstd for item in sublist]

    @property
    def files(self):
        return self._lst_files

    @files.setter
    def files(self, list_file):
        self._lst_files=list_file.copy()

    @property
    def size(self):
        return len(self._lst_files)

    @property
    def filtered_files(self):
        return list(filter(lambda x: self._check_file(x), self._lst_files))

    def filters(self, *fltrs):
        for f in fltrs:
            if not issubclass(type(f), FFilter):
                raise TypeError
            else:
                self._filters.setdefault(f.name, f)

    def _check_file(self, strFile):
        black_filters=[v for k, v in self._filters.items() if v.is_on and v.black]
        white_filters = [v for k, v in self._filters.items() if v.is_on and not v.black]
        #white_filters = list(filter(lambda x: not x.black, self._filters))
        return not any([f.check(strFile) for f in black_filters]) and all([f.check(strFile) for f in white_filters])

    def files_info(self, do_filter=True):
        lst=self.filtered_files if do_filter else self._lst_files
        lst_res=list()
        for f in lst:
            try:
                res=os.stat(f)
                lst_res.append({'file':f, 'ext':os.path.splitext(f)[-1].lower(),
                             'size':res.st_size, 'create_date':dt.datetime.fromtimestamp(res.st_ctime),
                             'mod_date':dt.datetime.fromtimestamp(res.st_mtime), 'last_acc_date':dt.datetime.fromtimestamp(res.st_atime)})
            except FileNotFoundError:
                continue
        return lst_res

    @property
    def work_path(self):
        return self._strPath

    def switch_filter(self, filter_name='', switch_value=True):
        self._filters[filter_name].is_on=switch_value

    def __str__(self):
        strF='\n\t'.join([str(v) for k, v in self._filters.items()])
        strR='''File list from: {path}
============================
filters:
    {filters}'''.format(path=self._strPath, filters=strF)
        return strR

def main():
    lstf=FileList('d:\Proba')
    black_list=x_extension_list(name='excl. ext', lst_ext=['db', 'exe', 'psd', 'arw'])
    white_list=x_extension_list(name='only ext', lst_ext=['jpg', 'jpeg', 'png'], black=False)
    black_dirs=x_folders(name='excl. dirs', lst_folders=[r'facebook\images', r'd:\proba\Yandex\2011\sc',
                                                         r'P\Photos (2)\worked', 'Подшипник Мебиуса _ Иллюзии_files'])
    white_dirs = x_folders(name='only dirs', lst_folders=[r'Lori', r'arts'], black=False)

    # print(black_dirs)
    # print(white_dirs)

    black_names=x_names(name='excl. names', lst_names=['-22',])
    white_names=x_names(name='only names', lst_names=['Untitled',], black=False)
    archive = x_archive(name='archive')
    # print(archive)

    f_lst=[black_list, white_list, black_dirs, black_names, white_names, archive]

    for f in f_lst:
        strF=str(f)
        print(strF)

    lstf.filters(black_list, white_list, black_dirs, white_dirs, black_names, white_names, archive)
    lstf.switch_filter(filter_name='archive', switch_value=False)
    lstf.switch_filter(filter_name='only names', switch_value=False)

    lstf.scan()

    # for fl in lstf.filtered_files:
    #     print(fl)
    for i in lstf.files_info(do_filter=True):
        print(i)

    print(lstf)


if __name__ == "__main__":
    # main()
    ft=x_ge_change_date(days_num=20)

    flst=FileList(r'U:\Solntsev\4site\New')

    flst.scan()

    for f in flst.files:
        print(f, ft.check(f))



