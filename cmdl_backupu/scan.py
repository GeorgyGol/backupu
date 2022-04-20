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

from cmdl_backupu.filters import *

FILE_INFO = ['path', 'change_date', 'create_date', 'size', 'mode', 'ext', 'A-attr', 'name']

def file_info(item: str) -> dict:
    """
    return dict() with file metadata
    :param item: str or pathlike - path to file; file must exists
    :return: dict with file info: path, change date, create date, size in bytes, mode, extension, file name, arhive attrubute
    :raise - errors from os.stat
    """
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

    return {FILE_INFO[0]: item, FILE_INFO[1]: dt.datetime.fromtimestamp(st.st_mtime),
            FILE_INFO[2]: dt.datetime.fromtimestamp(st.st_ctime),
            FILE_INFO[3]: st.st_size, FILE_INFO[4]: st.st_mode, FILE_INFO[5]: item.split('.')[-1], FILE_INFO[6]: isA,
            FILE_INFO[7]: Path(item).stem}


class xScan():
    """
    class for scanning source dir with sub-dirs;
    making list of files attribs;
    reseive list (or item by item) of filters for files (various - based on re for file name or date, or scpec. attr
    return filtered or un-listered list of files attribs;
    """

    def __init__(self, start_path: str = os.getcwd()):
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

    def _filtered_files(self) -> list:
        """
        self.scan scanning given path, make class-internal file list, un-filterd, all-files (without empty dirs)
        htis function apply all class filter (WHITEs first) on saved all-files list and return filtered list
        :return: filtered list of files
        """

        def white_apply(files):
            fltWhite = list(filter(lambda x: x.color == filter_color.WHITE, self._filters))
            if fltWhite:
                res = list()
                for fW in fltWhite:
                    res += list(filter(fW.s_check, files))
                return res
            else:
                return files

        def black_apply(files):
            fltBlack = list(filter(lambda x: x.color == filter_color.BLACK, self._filters))
            if fltBlack:
                res = files
                for fB in fltBlack:
                    res = list(filter(fB.s_check, res))
                return res
            else:
                return files

        def red_apply(files):
            """ red means exact"""
            fltRed = list(filter(lambda x: x.color == filter_color.RED, self._filters))
            if fltRed:
                res = files
                for fB in fltRed:
                    res = list(filter(fB.s_check, res))
                return res
            else:
                return files

        res = red_apply(black_apply(white_apply(self._lst_files)))

        _ = {f['path']: f for f in res}  # for drop path duplicates
        return list(_.values())

    def files(self, filtered: bool = False) -> list:
        """
        return list of scanned files (list of dict with file attr)
        :param filtered: True - return filtered list, False - scanned
        :return: list of dicts with file attrib
        """
        if filtered:
            return self._filtered_files()
        else:
            return self._lst_files

    def scan(self) -> list:
        """
        scan source base path and making list of files
        :return: list of files with file info (full name + attribs)
        """
        lstd = [[os.path.join(i[0], f) for f in i[2]] for i in os.walk(self.base_path)]
        self._lst_files = [file_info(item) for sublist in lstd for item in sublist]

        return self._lst_files

    @property
    def filters(self) -> list:
        """
        :return: list of all filters in class
        """
        return self._filters

    def set_filters(self, *argc):
        """
        clear filter list, setup it from params
        :param argc: filters object based on abcFilter
        :return:
        """
        assert len(list(
            filter(lambda x: not isinstance(x, abcFilter), argc))) == 0, 'all params must be based on abcFilter class'

        self._filters = list()
        self._filters += argc
        for f in self._filters:
            f.BasePath = self._base_path

    def print_files(self, filtered=True):
        for f in self.files(filtered=filtered):
            print(f)

    def size(self, filtered=True):
        return len(self.files(filtered=filtered))


def scan():
    # some examples
    # create xScan object

    # --- for scanning selected dir
    sc = xScan(start_path=r'/home/egor/git/jupyter/housing_model')

    # --- for scanning current dir
    # sc = xScan()
    sc.scan()
    print(sc.base_path)

    # set up filters
    # --- file full path filters
    fPathW = filterFilePath(color=filter_color.WHITE, case=string_case.ANY, rule=r'\\PY\\')
    fPathB = filterFilePath(color=filter_color.BLACK, case=string_case.STRICT, rule=r'\\\.')

    # --- file name filters (only name from full path)
    fNameW = filterFileName(color=filter_color.WHITE, case=string_case.STRICT, rule=r'_')
    fNameB = filterFileName(color=filter_color.BLACK, case=string_case.STRICT, rule=r'test')

    # --- file ext filters (only ext from full path)
    fExtW = filterFileExt(color=filter_color.WHITE, case=string_case.STRICT, rule=r'py.*')
    fExtB = filterFileExt(color=filter_color.BLACK, case=string_case.STRICT, rule=r'pyc')

    # --- file dir filters (only parend dir name from full path)
    fDirW = filterDirName(color=filter_color.WHITE, case=string_case.ANY, rule=r'PY')
    fDirB = filterDirName(color=filter_color.BLACK, case=string_case.ANY, rule=r'\\aigk\\PY')

    # --- file size filters
    fSizeW = filterFileSize(color=filter_color.WHITE, low_level=10, high_level=5e3)
    fSizeB = filterFileSize(color=filter_color.BLACK, low_level=50)

    # --- file archive attribute filters
    fAAtrW = filterArchAttrib(color=filter_color.WHITE)
    fAAtrB = filterArchAttrib(color=filter_color.BLACK)

    fDtRangeW = filterFileDateRange(color=filter_color.WHITE,
                                    low_date=dt.date(day=1, month=1, year=2018),
                                    high_date=dt.date(day=1, month=1, year=2020))
    fDtRangeB = filterFileDateRange(color=filter_color.BLACK,
                                    low_date=dt.date(day=1, month=1, year=2018),
                                    high_date=dt.date(day=1, month=1, year=2020))

    fDtW = filterFileDateExact(color=filter_color.WHITE,
                               file_date=dt.date(day=2, month=3, year=2017))

    fDtB = filterFileDateExact(color=filter_color.BLACK,
                               file_date=dt.date(day=2, month=3, year=2017))

    # set up list of filters
    filters = [
        filterFilePath(color=filter_color.WHITE, case=string_case.STRICT, rule=r'\.py\b'),
        filterFilePath(color=filter_color.BLACK, case=string_case.STRICT, rule=r'__init__')
    ]

    # set filters property for xScan
    # sc.set_filters(fDirB, fDirW)
    # sc.set_filters(fDtW)
    # sc.set_filters(*filters)

    filters = [filterFileExt(color=filter_color.WHITE, rule=r'sqlite\d?'),
               filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb')]

    sc.set_filters(*filters)
    # cw.scanner.set_filters(*filters)

    # print filters from xScan
    for f in sc.filters:
        print(f)

    # get filtered file list
    fl = sc.files()  # unfilterd scanned files
    ffl = sc.files(filtered=True)  # filterd scanned files (apply all filters)
    #
    for f in ffl:
        print(f['path'], f['change_date'], f['ext'])

    print('all files - ', sc.size(filtered=False), 'filteres - ', sc.size(filtered=True))


if __name__ == "__main__":
    # scan()
    # for f in os.listdir('..'):
    #     print(f)

    print('All done')
