"""using FileList class from scan module for making pandas dataframe from scanned and filtered file list
can save dataframe in csv-file, can group files by extensions with size-of-files sum
can summarize files sum without grouping
return dataframe for ather analisys"""

import pandas as pd

from cmdl_backpz import scan


class FolderInfo():
    _file_list=None
    _pdf=None

    def __init__(self, strPath, *filters, **kwargs):
        self._file_list= scan.FileList(strPath)
        self._file_list.filters(*filters)
        if kwargs:
            self._file_list.files=kwargs['file_list']

    def scan(self, do_filter=True):
        self._file_list.scan()
        self._pdf=pd.DataFrame(self._file_list.files_info(do_filter=do_filter))


    @property
    def work_path(self):
        return self._file_list.work_path

    @property
    def extensions(self):
        return self._pdf['ext'].sort_values().unique().tolist()

    @property
    def dataframe(self):
        return self._pdf

    def sum(self):
        # in Mbt
        return self._pdf['size'].sum() / 1e6

    def to_csv(self, file_name=''):
        strFile=file_name if file_name else self.work_path.replace('\\', '_').replace(':', '')+'.csv'
        self._pdf.to_csv(strFile, sep=';')

    def sum_ext(self):
        return self._pdf.groupby('ext')['size'].sum().sort_values()

    def __str__(self):
        strRet = '''
FOLDER-FILES INFO
SOURCE PATH - {s_path} 
{files_info}
========================================'''.format(s_path=self._file_list.work_path,
                                                   files_info=str(self._file_list))
        return strRet

def main():
    black_dirs = scan.x_folders(name='excl. dirs', lst_folders=[r'@Recycle', ])

    #xinfo = FolderInfo(r'\\Commd\Personal', black_dirs)
    xinfo = FolderInfo(r'\\l26-srv0\h$\U\INC_29_01_2020', black_dirs)

    print(xinfo)

    print('start scanning ', xinfo.work_path)
    xinfo.scan()

    #
    print('extensions :', xinfo.extensions)
    print('Full size: ', xinfo.sum())

    xinfo.to_csv(file_name='f_u_inc_files.csv')
    ext=xinfo.sum_ext()
    print(ext)
    ext.to_csv('f_u_inc_exts.csv', sep=';', encoding='cp1251')

    #pdf.to_csv('u_gg_view.csv', sep=';')

    print(xinfo.dataframe[xinfo.dataframe['ext']=='.csv'])
    print(xinfo.dataframe[xinfo.dataframe['ext'] == '.accdb'])

if __name__ == "__main__":
    main()
