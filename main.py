import datetime as dt
import os
import re
import subprocess
import shutil
import pandas as pd
import argparse

from cmdl_backpz.info import FolderInfo

strWorkPath=r'd:\proba'
black_lst_ext=['db', 'exe', 'psd']
white_lst_ext=['jpg', 'jpeg', 'png', 'gif']

black_lst_dirs=[r'facebook\images', r'd:\proba\Yandex\2011\sc', r'P\Photos (2)\worked']
black_names_list=['\~\$', ]

class XBackup:
    _strBasePath=''
    _strSavePath = ''
    _lst_black_ext=[]
    _lst_white_ext=[] # has priority over black
    _lst_black_dirs=[]
    _lst_black_names=[] # '~$'

    _name=''

    _lst_files=[]

    def __init__(self, strBasePath, strSavePath='',  name='', black_list_ext=[],
                 white_list_ext=[], black_list_dirs=[], black_names=[]):
        self._strBasePath = strBasePath
        self._strSavePath = strSavePath
        if self._strBasePath == self._strSavePath:
            raise FileExistsError('Source "{0}" equals to target "{1}"'.format(self._strBasePath, self._strSavePath))

        self._lst_black_ext = black_list_ext
        self._lst_white_ext = white_list_ext
        self._lst_black_dirs= black_list_dirs
        self._lst_black_names=black_names
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def base_path(self):
        return self._strBasePath

    @property
    def save_path(self):
        return self._strSavePath

    @property
    def black_list_extentions(self):
        return self._lst_black_ext

    @black_list_extentions.setter
    def black_list_extentions(self, lst):
        self._lst_black_ext=lst

    @property
    def white_list_extentions(self):
        return self._lst_white_ext

    @white_list_extentions.setter
    def white_list_extentions(self, lst):
        self._lst_white_ext=[i.replace('.', '') for i in lst]

    def __str__(self):
        return '''
Backup work unit:
    Name:       {name},
    SourceDir:  {src_dir}, 
    TargetDir:  {trg_dir},
    Black list: {black_lst},
    White list: {white_list}, 
    Excl. dirs: {black_dirs},
    Black names:{black_names} 
==============================
        '''.format(name=self._name, src_dir=self._strBasePath, trg_dir=self._strSavePath, black_names=self._lst_black_names,
                   black_dirs=self._lst_black_dirs, white_list=self._lst_white_ext, black_lst=self._lst_black_ext)


    @property
    def black_dirs(self):
        return self._lst_black_dirs
    @black_dirs.setter
    def black_dirs(self, lst):
        print(lst)
        lst_dirs = list(map(os.path.splitdrive, lst))
        lst_dirs = [os.path.join(i[0] if i[0] else self._strBasePath, i[1]) for i in lst_dirs]
        self._lst_black_dirs=lst_dirs

    @property
    def work_files(self):
        return self._lst_files

    #actions block======================================================================================================
    def _switch_archive(self, strPath, str_comm='-A'):
        subprocess.check_output(['attrib', str_comm, strPath])

    def scan(self, full=False):
        lstd = [[os.path.join(i[0], f) for f in i[2]] for i in os.walk(self._strBasePath)]
        self._lst_files = [item for sublist in lstd for item in sublist if self.check_file(item, full)]
        return self.work_files

    def backup(self, str_pre='', str_suff=dt.datetime.now().strftime('%d_%b_%Y'), on_exists='count', str_join='_'):
        if len(self.work_files)==0: return

        strWorkDir=self.get_sub_path(str_pre=str_pre, str_suff=str_suff, on_exists=on_exists, str_join=str_join)
        b_copy=on_exists=='copy'

        os.makedirs(strWorkDir, exist_ok=b_copy)

        sd = set(filter(lambda x: x!=strWorkDir, {os.path.dirname(f).replace(self._strBasePath, strWorkDir) for f in self._lst_files}))
        for d in sd:
            os.makedirs(d, exist_ok=True)
            #print(d)

        self._copy_files(strWorkDir)
        #return strWorkDir

    def _copy_files(self, strTarget):
        lst=[(f, f.replace(self._strBasePath, strTarget)) for f in self.work_files]
        for cf in lst:
            print('copy {0} to {1}...'.format(cf[0], cf[1]), end='')
            copy2(cf[0], cf[1])
            self._switch_archive(cf[0])
            print('done')
        return len(lst)

    def get_sub_path(self, str_pre='', str_suff='', on_exists='count', str_join='_'):
        str_sf=str_join.join(list(filter(lambda x: len(x)>0, [str_pre, str_suff])))

        if str_sf=='' and on_exists=='count':
            str_sf=str_join

        strt = os.path.join(self._strSavePath, str_sf)

        if os.path.exists(strt):
            if on_exists=='count':
                re_rule=re.compile(str_sf)
                lst_dirs=os.listdir(self._strSavePath)
                cnt=len(list(filter(re_rule.search, lst_dirs)))
                strt += '{0}{1}'.format(str_join, cnt - 1)
                if os.path.exists(strt):
                    lst_nums=[int(re.search(r'{0}(\d+)$'.format(str_join), i).group(1)) for i in list(filter(re_rule.search, lst_dirs))[1:]]
                    strt = re.sub(r'{0}\d+$'.format(str_join), sorted(lst_nums)[-1]+1, strt)
                return strt
            elif on_exists=='copy':
                return strt
        else:
            return strt

    #end actions========================================================================================================


    #check files block==================================================================================================

    def _check_archive(self, strPath):
        xr = subprocess.check_output(['attrib', strPath])
        try:
            return chr(xr[0]) == 'A'
        except IndexError:
            return False

    def _check_blacklist_file_ext(self, strPath):
        return os.path.splitext(strPath)[1].replace('.', '') in self._lst_black_ext

    def _check_whitelist_file_ext(self, strPath):
        if len(self._lst_white_ext)>0:
            return os.path.splitext(strPath)[1].replace('.', '') in self._lst_white_ext
        else:
            return True

    def _check_black_folder(self, strPath):
        return os.path.split(strPath)[0] in self._lst_black_dirs

    def _check_black_names(self, strPath):
        for i in self._lst_black_names:
            if re.search(i, strPath): return True
        return False

    def check_file(self, strPath, b_full, debug=False):
        archive = b_full or self._check_archive(strPath) # false if not backup, true - backup
        blackfolder = self._check_black_folder(strPath)
        whitelist=self._check_whitelist_file_ext(strPath)
        blacklist=self._check_blacklist_file_ext(strPath)
        blacknamelist=self._check_black_names(strPath)
        if debug:
            print('4 path: {5} -> archive {0}, blackfolder {1}, whitelist {2}, blacklist {3}, blackname {4}'.format(archive, blackfolder, whitelist,
                                                                                                blacklist, blacknamelist, strPath))

        return archive and whitelist and not blackfolder and not blacklist and not blacknamelist

    # end check block===================================================================================================




def main():
    x = XBackup(r'u:\golyshev', name='testing', strSavePath=r'g:\ggolyshev',
                black_list_ext=['csv', 'exe', 'accdb', 'msi', 'cab'],
                black_names=black_names_list)
    # x=XBackup(strWorkPath, name='testing', strSavePath=r'g:\test', black_list_ext=black_lst_ext,
    #            black_list_dirs=black_lst_dirs)

    print(x)

    # str1=r'u:\golyshev\NOTES\Conf_12\Доклад_12\~$кст_07_12.doc'
    # str2=r'u:\golyshev\NOTES\Conf_12\Доклад_12\нфДоклад_12.doc'

    # print(x.check_file(str1, False))
    # print(x.check_file(str2, True))

    lst=x.scan(full=True)

    # for i in lst:
    #     print(i)
    print('+'*60)
    xi=FolderInfo(x.base_path, lst_files=x.work_files)
    xi.scan()

    print(xi.sum())

    #x.copy_files(r'g:\test\inc_06_Dec_2019')
    #x.backup(str_pre='inc')
    #g:\test\inc_06_Dec_2019


if __name__ == "__main__":


    print(re.__version__)
#    print(subprocess.__version__)
#    print(shutil.__version__)
    print(pd.__version__)
    print(argparse.__version__)

    #main()



    #os.makedirs(r'g:\test', exist_ok=True)

    # strT=r'd:\proba\P\Photos (2)\worked\Thumbs.db'
    # strT=r'd:\proba\022240101l.jpg'
    # # print(check_blacklist_file_ext(strT))
    #
    # #print(check_black_folder(strT))
    # def make_sub_path(str_pre='', str_suff='', on_exists='count'):
    #     strBase=r'g:\test'
    #
    #     str_sf='_'.join(list(filter(lambda x: len(x)>0, [str_pre, str_suff])))
    #
    #     if str_sf=='':
    #         if on_exists=='count':
    #             str_sf='_'
    #
    #     strt = os.path.join(strBase, str_sf)
    #     try:
    #         os.makedirs(strt)
    #     except FileExistsError:
    #         if on_exists=='count':
    #             re_rule=re.compile(str_sf)
    #             lst_dirs=os.listdir(strBase)
    #             cnt=len(list(filter(re_rule.search, lst_dirs)))
    #             strt += '_{0}'.format(cnt - 1)
    #             try:
    #                 os.makedirs(strt)
    #             except FileExistsError:
    #                 lst_nums=[int(re.search(r'_(\d+)$', i).group(1)) for i in list(filter(re_rule.search, lst_dirs))[1:]]
    #                 strt = re.sub(r'_\d+$', sorted(lst_nums)[-1]+1, strt)
    #                 os.makedirs(strt)
    #         elif on_exists=='copy':
    #             return str_sf
    #
    #     print(strt)
    #
    #
    #
    # #print(dt.datetime.now().strftime('%d_%b_%Y'))
    #
    # print(get_sub_path(str_pre='inc', str_suff=dt.datetime.now().strftime('%d_%b_%Y')))
    #print(get_sub_path(on_exists='copy'))
    #make_sub_path(on_exists='copy')

    #print(os.chflags(strT))
    print('All done')



