"""
The module contains classes for scanning the selected operating system directory (including shared network) and filters for scanned files
Files are scanned into a list with full names (including paths)
Filters inherit from an abstract class.
The module has 4 main filters
"""

import errno

from cmdl_backpz.filters import *


class xScan():

    def __init__(self, start_path=os.getcwd()):
        if os.path.isdir(start_path):
            self._base_path = start_path
            self._filters = list()
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), start_path)

    @property
    def base_path(self):
        return self._base_path

    def _filtered_files(self):
        fltWhite = list(filter(lambda x: x.color == filter_color.WHITE, self._filters))
        fltBlack = list(filter(lambda x: x.color == filter_color.BLACK, self._filters))

        lstFls = self._lst_files
        for fW in fltWhite:
            lstFls = list(filter(fW.s_check, lstFls))

        for fB in fltBlack:
            lstFls = list(filter(fB.s_check, lstFls))

        return lstFls

    def files(self, filtered=False):
        if filtered:
            return self._filtered_files()
        else:
            return self._lst_files

    def scan(self, with_info=True):
        def info(item):
            st = os.stat(item)
            # x = dt.datetime.fromtimestamp(st.st_mtime).date()
            try:
                if platform.system() == 'Windows':
                    xr = subprocess.check_output(['attrib', item])
                    isA = self._check_func(chr(xr[0]), 'A')
                else:
                    isA = False
            except IndexError:
                isA = False

            return {'path': item, 'change_date': dt.datetime.fromtimestamp(st.st_mtime).date(),
                    'create_date': dt.datetime.fromtimestamp(st.st_ctime).date(),
                    'size': st.st_size, 'mode': st.st_mode, 'ext': item.split('.')[-1], 'A-attr': isA}

        lstd = [[os.path.join(i[0], f) for f in i[2]] for i in os.walk(self.base_path)]
        if with_info:
            self._lst_files = [info(item) for sublist in lstd for item in sublist]
        else:
            self._lst_files = [item for sublist in lstd for item in sublist]

        # for i in self._lst_files:
        #     print(i)
        return self._lst_files

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, f):
        assert isinstance(f, abcFilter) or (f == None)
        if f:
            self._filters.append(f)
        else:
            self._filters = list()

    def set_filters(self, *argc):
        for f in argc:
            if not isinstance(f, abcFilter):
                raise TypeError
        for f in argc:
            self._filters.append(f)

    def print_files(self, filtered=True):
        for f in self.files(filtered=filtered):
            print(f)


def scan():
    # sc = xScan(start_path='/home/egor/git/jupyter')
    sc = xScan(start_path='/media/egor/docs')
    fPath = fDirName(color=filter_color.WHITE, rules={'Reelroad', 'Norah Jones'})
    fName = fFileName(rules='\d+', subtype=filter_subtype.NAME)
    fExt = fFileName(rules='mp3', color=filter_color.WHITE)

    sc.set_filters(fPath, fExt, fName)

    sc.scan()
    for f in sc.filters:
        print(f)
    print('=' * 50)
    sc.print_files()


if __name__ == "__main__":
    # main()

    # if not os.path.ismount("smb://commd.local/personal/Golyshev"):
    #     print("not yet, mounting...")
    #     os.system("mount smb://commd.local/personal/Golyshev")

    scan()
    # ft=x_ge_change_date(days_num=20)
    #
    # flst=FileList(r'U:\Solntsev\4site\New')
    #
    # flst.scan()
    #
    # for f in flst.files:
    #     print(f, ft.check(f))
    print('All done')
