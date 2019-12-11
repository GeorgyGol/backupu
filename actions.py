import scan
import os
import info

from abc import ABC, abstractmethod

import subprocess
import datetime as dt
import re
from shutil import copyfile, copy2
from info import FolderInfo

class X_SPATH(ABC):
    _base_path=''
    def __init__(self, strBasePath):
        self._base_path=strBasePath

    @abstractmethod
    def subpath(self, *args, **kwargs):
        pass

class x_path_date_inc(X_SPATH):
    _str_pre=''
    _str_suff=''
    _str_dele='_'

    def __init__(self, strBasePath, prefix='', delimiter='_', month_format='%m'):
        self._base_path=strBasePath
        self._str_pre=prefix
        self._str_suff=dt.datetime.now().strftime(self._str_dele.join(['%d', month_format, '%Y']))
        self._str_dele = delimiter

    def _check_exists(self, strPath):
        if os.path.exists(strPath):
            lst_dirs = os.listdir(self._base_path)
            re_last=re.compile('{dele}{dele}(\d+)$'.format(dele=self._str_dele))
            try:
                num=sorted([int(re_last.search(p).group(1)) for p in filter(re_last.search, lst_dirs)])[-1]+1
            except IndexError:
                num=0
            return strPath + self._str_dele*2 + str(num)
        else:
            return strPath

    def subpath(self, *args, **kwargs):
        try:
            self._str_pre=kwargs['prefix']
        except:
            pass
        strPrePath=os.path.join(self._base_path, '{pre}{dele}{suff}'.format(pre=self._str_pre,
                                                                       suff=self._str_suff,
                                                                       dele=self._str_dele))
        return self._check_exists(strPrePath)

class x_path_copy(X_SPATH):
    def subpath(self):
        return self._base_path

class XBackup_A:
    _files=None
    _strSavePath=''
    _name=''
    _sub_path_rule=None
    _pre_subpath=list()

    def __init__(self, strWorkPath='', strSavePath='',
                 SaveSubFolderRule=None, name='', prefixses=list(), *filters):
        if strSavePath.startswith(os.path.abspath(strWorkPath)):
            raise FileExistsError('Can\'t backup to working folder: {0} -> {1}'.format(strWorkPath, strSavePath))
        self._strSavePath=strSavePath
        self._files=scan.FileList(strWorkPath)
        self._sub_path_rule=SaveSubFolderRule
        if len(prefixses) < 2:
            self._pre_subpath = ['FULL', 'INC']
        else:
            self._pre_subpath=prefixses
        self._name=name

    def filters(self, *filters):
        f_arch = scan.x_archive('archive')
        self._files.filters(f_arch, *filters)

    @property
    def name(self):
        return self._name
    @property
    def work_path(self):
        return self._files.work_path
    @property
    def save_path(self):
        return self._strSavePath

    def __str__(self):
        strRet='''
BACKUP {name} 
SAVE PATH - {path}
sub-path prefixes: for full copy - {pre_full}, for inc-copy - {pre_inc} 
{files_info}
========================================'''.format(name=self._name, path=self._strSavePath,
                                                   files_info=str(self._files), pre_full=self._pre_subpath[0],
                                                   pre_inc=self._pre_subpath[1])
        return strRet

    def scan(self, full=False):
        self._files.scan()
        if full:
            self._files.switch_filter(filter_name='archive', switch_value=False)
            return self._files.filtered_files
        else:
            self._files.switch_filter(filter_name='archive', switch_value=True)
            return self._files.filtered_files

    def _switch_archive(self, strPath, str_comm='-A'):
        subprocess.check_output(['attrib', str_comm, strPath])

    def backup(self, full=False):
        print(self)

        lst_files=self.scan(full=full)
        if len(lst_files)==0: return []

        if full:
            strWorkDir=self._sub_path_rule.subpath(prefix=self._pre_subpath[0])
        else:
            strWorkDir = self._sub_path_rule.subpath(prefix=self._pre_subpath[1])

        os.makedirs(strWorkDir)

        work_list=[(f, f.replace(self._files.work_path, strWorkDir)) for f in lst_files]
        new_folders=set([os.path.dirname(pr[1]) for pr in work_list])
        for dir in new_folders:
            os.makedirs(dir, exist_ok=True)
        print('RUN FOR {} FILES...'.format(len(lst_files)))
        for i, pair in enumerate(work_list):
            print('\t{2} from {3}:\tcopy {0} to {1}...'.format(pair[0], pair[1], i, len(work_list)), end='')
            copy2(pair[0], pair[1])
            self._switch_archive(pair[0])
            print('done')
        print('DONE')
        return work_list



def main():
    # f_extb = scan.x_extension_list(name='excl ext', lst_ext=['accdb', 'csv', 'xml', 'psd'])
    # f_dirb = scan.x_black_folders(name='excl dirs', lst_folders=['Salnikov', 'from di', 'chat_log'])

    # strSourceDir=r'u:\golyshev'
    # strTargetDir=r'g:\u_golyshev'

    strSourceDir = r'd:\proba'
    strTargetDir = r'g:\egor'

    f_extb = scan.x_extension_list(name='excl ext', lst_ext=['arw', 'psd', 'db', ''])
    f_dirb = scan.x_black_folders(name='excl dirs', lst_folders=['Подшипник Мебиуса _ Иллюзии_files', 'lori', 'сайт'])

    x_subpath=x_path_date_inc(strTargetDir, prefix='INC', month_format='%b')

    x = XBackup_A(strWorkPath=strSourceDir, name='testing', strSavePath=strTargetDir, SaveSubFolderRule=x_subpath)
    x.filters(f_extb, f_dirb)

    #print(x)
    x.backup(full=True)
    # lst_files=x.scan(full=True)
    # for fl in lst_files:
    #     print(fl)
    # print('*'*50)
    # x_info=info.FolderInfo(x.work_path, file_list=lst_files)
    # x_info.scan()
    #
    # print('sum - ', x_info.sum())
    # print(x_info.sum_ext())

if __name__ == "__main__":
    # xp=x_path_date_inc(r'g:\u_golyshev', prefix='INC', month_format='%b')
    # print(xp.subpath())
    # xp_copy=x_path_copy(r'g:\u_golyshev')
    # print(xp_copy.subpath())
    main()
    #print(re.search(r'u\:\\golyshev', r'u\:\\golyshev\\Salnikov'))

