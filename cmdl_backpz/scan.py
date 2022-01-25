"""
The module contains class for scanning the selected operating system directory (including shared network)
Files are scanned into a list of dictionary with full name (including paths) and file's attribs:
    path - full path
    change_date
    create_date
    size - in bytes
    mode
    ext - file extension
    A-attr - MS Windows specific archive attribute
"""

import errno
import platform
import os
import subprocess
import datetime as dt

# import sys
# v_info = sys.version_info
# print(v_info[0], v_info[1])

from cmdl_backpz.filters import *

class xScan():
    """
    class for scanning source dir with sub-dirs;
    making list of files attribs;
    reseive list (or item by item) of filters for files (various - based on re for file name or date, or scpec. attr
    return filtered or un-listered list of files attribs;
    """
    def __init__(self, start_path:str=os.getcwd()):
        if os.path.isdir(start_path):
            self._base_path = start_path
            self._filters = list()
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), start_path)

    @property
    def base_path(self):
        """
        :return:  self._base_path - source working path
        """
        return self._base_path

    def _filtered_files(self)->list:
        """
        self.scan scanning given path, make class-internal file list, un-filterd, all-files (without empty dirs)
        htis function apply all class filter (WHITEs first) on saved all-files list and return filtered list
        :return: filtered list of files
        """
        fltWhite = list(filter(lambda x: x.color == filter_color.WHITE, self._filters))
        fltBlack = list(filter(lambda x: x.color == filter_color.BLACK, self._filters))

        lstFls = self._lst_files
        for fW in fltWhite:
            lstFls = list(filter(fW.s_check, lstFls))

        for fB in fltBlack:
            lstFls = list(filter(fB.s_check, lstFls))

        return lstFls

    def files(self, filtered:bool=False)->list:
        """
        return list of scanned files (list of dict with file attr)
        :param filtered: True - return filtered list, False - scanned
        :return: list of dicts with file attrib
        """
        if filtered:
            return self._filtered_files()
        else:
            return self._lst_files

    def scan(self)->list:
        """
        scan source base path and making list of files
        :return: list of files with file info (full name + attribs)
        """
        def info(item):
            st = os.stat(item)
            # x = dt.datetime.fromtimestamp(st.st_mtime).date()
            try:
                if platform.system() == 'Windows':
                    xr = subprocess.check_output(['attrib', item])
                    isA = chr(xr[0]) == 'A'
                else:
                    isA = False
            except IndexError:
                isA = False

            return {'path': item, 'change_date': dt.datetime.fromtimestamp(st.st_mtime).date(),
                    'create_date': dt.datetime.fromtimestamp(st.st_ctime).date(),
                    'size': st.st_size, 'mode': st.st_mode, 'ext': item.split('.')[-1], 'A-attr': isA}

        lstd = [[os.path.join(i[0], f) for f in i[2]] for i in os.walk(self.base_path)]
        self._lst_files = [info(item) for sublist in lstd for item in sublist]

        return self._lst_files

    @property
    def filters(self)->list:
        """

        :return: list of all filters in class
        """
        return self._filters

    @filters.setter
    def filters(self, f):
        """
        append param to filter-list
        :param f: filter base on abcFilter
        :return: None
        """
        assert isinstance(f, abcFilter) or (f == None)
        if f:
            self._filters.append(f)
        else:
            self._filters = list()

    def set_filters(self, *argc):
        """
        append params to filter-list
        :param argc: filters object based on abcFilter
        :return:
        """
        for f in argc:
            if not isinstance(f, abcFilter):
                raise TypeError
        for f in argc:
            self._filters.append(f)

    def print_files(self, filtered=True):
        for f in self.files(filtered=filtered):
            print(f)

    def size(self, filtered=True):
        return len(self.files(filtered=filtered))




def scan():
    # sc = xScan(start_path='/home/egor/git/jupyter')
    # sc = xScan(start_path=r'U:\Golyshev\Py')
    sc = xScan()
    print(sc.base_path)
    start_pos = len(sc.base_path)
    # fPathW = fFilePath(color=filter_color.WHITE, case=string_case.STRICT, rules=r'\\CarSales\\', start_position=start_pos)
    # fPathB = fFilePath(color=filter_color.BLACK, case=string_case.STRICT, rules=r'\\\.', start_position=start_pos)

    # fPath = fDirName(color=filter_color.WHITE, rules={'Reelroad', 'Norah Jones'})
    # fName = fFileName(rules='\d+', subtype=filter_subtype.NAME)
    # fExt = fFileName(rules='mp3', color=filter_color.WHITE)
    #
    # sc.set_filters(fPathW, fPathB)
    filters = [
        fFilePath(color=filter_color.WHITE, case=string_case.STRICT, rules=r'\.py\b', start_position=start_pos),
        fFilePath(color=filter_color.BLACK, case=string_case.STRICT, rules=r'\\__init__', start_position=start_pos)
    ]
    sc.set_filters(*filters)
    sc.scan()
    # for f in sc.filters:
    #     print(f)
    print('=' * 50)
    sc.print_files(filtered=True)
    print('all files - ', sc.size(filtered=True))


if __name__ == "__main__":
    # main()

    # if not os.path.ismount("smb://commd.local/personal/Golyshev"):
    #     print("not yet, mounting...")
    #     os.system("mount smb://commd.local/personal/Golyshev")

    print(scan())
    # ft=x_ge_change_date(days_num=20)
    #
    # flst=FileList(r'U:\Solntsev\4site\New')
    #
    # flst.scan()
    #
    # for f in flst.files:
    #     print(f, ft.check(f))
    print('All done')
