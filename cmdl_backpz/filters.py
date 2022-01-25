"""
definitions for classes of filters for filtering scanned files list from class xScan (module scan this project)
all these classes is supposed to be used in the class xScan to filter the list obtained when scanning by
this class - a list of dictionaries with file attributes (name, full path, date, size, etc.)

    ONE RULE = ONE FILTER

    all filters based on abstract class abcFilter;
    filters can be BLACK or WHITE: White means 'only selected rules', Black means 'all but selected rules'
    WHITE filters applyes first

    filters in this module are:
       on file name - by re
       on file path - by re
       on dir path - by re
       on file extension - by re
       on file size - exactly or range
       on file date - exactly or range
       on os windows specific archive file attrib

    all filters have function 'check' that have one param 'item': checks for compliance item with the filter rule
    for filtering specific xScan file list all filters have function 's_check' that have one param 'item':
                checks for compliance named item (dict item) with the filter rule

    usage filter object on list of some items like this:
        result_filtering = list(filter(x_filter.check, items_list))
"""
import datetime as dt
import operator as op
import os
import pathlib
import re
import subprocess
from abc import ABC, abstractmethod

from enum import Enum#, auto

class filter_type(Enum):
    PATH = 1 #auto()
    DIR = 2
    FILE = 3
    ATTRIB = 4
    DATE = 5
    SIZE = 6


class filter_subtype(Enum):
    NAME = 1
    EXT = 2
    DATE_MARGIN = 3
    SIZE_MARGIN = 4
    DATE_EXACT = 5


class string_case(Enum):
    STRICT = 1
    ANY = 2


class filter_color(Enum):
    WHITE = 1
    BLACK = 2


class abcFilter(ABC):
    """  base class for all filters  """
    def __init__(self, color:filter_color=filter_color.WHITE):
        assert isinstance(color, filter_color)
        self._color = color

    @property
    def type(self)->filter_type:
        return self._type

    @property
    def subtype(self)->filter_subtype:
        return self._subtype

    @property
    def color(self)->filter_color:
        return self._color

    @abstractmethod
    def _compile(self):
        """
        compile filter rule - commonly filter re-expression
        """
        pass

    @abstractmethod
    def check(self, item:str)->bool:
        """
        function for make filtering - apply rule to item and return bool result filtering
        :param item:
        :return: filtering result
        """
        pass

    @abstractmethod
    def s_check(self, item:dict)->bool:
        """
        function for make filtering - apply rule to item and return bool result filtering
        :param item: dict with file properties from xScan.scan()
        :return: filtering result
        """
        pass

    @property
    def rules(self):
        return self._rules

    def __str__(self):
        # for python 3.10 ->
        # return f'{self.color.name} filter on {self.type.name} ({self.subtype.name}); rules = {self.rules}'

        _s = '{color} filter on {type} ({subtype}); rules = {rules}'
        return _s.format(color = self.color.name, type = self.type.name,
                         subtype = self.subtype.name, rules = self.rules)


# file path-names filters - using re
class fFilePath(abcFilter):
    """
    class for filter on file path and name, working on item['path'] scanned file list, for rule use re-eexpressions
    base class for filtering on name, dirs and extension classes
    """

    def __init__(self, color=filter_color.BLACK, subtype=filter_subtype.EXT,
                 case=string_case.STRICT, rules:str='', start_position:int=0):
        """

        :param color: BLACK or WHITE for 'only but' or 'only' items
        :param subtype: name | dir | ext part of full file name
        :param case: case sensivity (key (?i) in re)
        :param rules: re-eexpression for filtering
        :param start_position: starting position for re-search
        """
        assert isinstance(subtype, filter_subtype)
        assert isinstance(case, string_case)

        super().__init__(color=color)

        self._type = filter_type.PATH
        self._subtype = subtype
        self._case = case

        self._rules = rules
        self._str_pre = '(?i)' if self.case == string_case.ANY else ''

        self._search = '' # prepared and compiled re-object
        self._start_position = start_position

        self._compile()

        if self.color == filter_color.BLACK:
            self._check_func = lambda item: self._search.search(item) is None
        else:
            self._check_func = lambda item: self._search.search(item) is not None

    @property
    def case(self):
        """
        :return: filter case-sensivity
        """
        return self._case

    def __str__(self):
        # for Python 3.10 ->
        # return super().__str__() + f'; string case: {self.case.name}'
        _s = '; string case: {case}'
        return super().__str__() + _s.format(case = self.case.name)

    def check(self, item):
        return self._check_func(item)

    def s_check(self, item):
        return self._check_func(item['path'])

    def _compile(self):
        strF = self._str_pre + self._rules
        self._search = re.compile(strF, self._start_position)
        return self._search


class fFileName(fFilePath):

    def __init__(self, color=filter_color.BLACK, subtype=filter_subtype.EXT,
                 case=string_case.STRICT, rules=set()):
        super().__init__(color=color, subtype=subtype, case=case, rules=rules)
        self._type = filter_type.FILE

        if self.subtype == filter_subtype.EXT:
            if self.color == filter_color.BLACK:
                self._check_func = lambda x: self._search.search(x) is None
            else:
                self._check_func = lambda x: self._search.search(x) is not None
        else:  # self.subtype == filter_subtype.NAME:
            if self.color == filter_color.BLACK:
                self._check_func = lambda x: self._search.search(pathlib.Path(x).stem) is None
            else:
                self._check_func = lambda x: self._search.search(pathlib.Path(x).stem) is not None

    def _compile(self):
        if self.subtype == filter_subtype.EXT:
            # поиск по расширениям файлов

            strF = '\.' + '|'.join(set(map(lambda x: str(x), self.rules))) + '$'
            self._make_re(strF)
        else:  # self.subtype == filter_subtype.NAME:
            # поиск по именам файлов
            strF = '|'.join(set(map(lambda x: str(x), self.rules)))
            self._make_re(strF)


class fDirName(fFilePath):
    def __init__(self, color=filter_color.BLACK,
                 case=string_case.STRICT, rules=set()):
        super().__init__(color=color, subtype=filter_subtype.NAME, case=case, rules=rules)
        self._type = filter_type.DIR

        if self.color == filter_color.BLACK:
            self._check_func = lambda x: self._search.search(str(pathlib.Path(x).parent)) is None
        else:
            self._check_func = lambda x: self._search.search(str(pathlib.Path(x).parent)) is not None

    def _compile(self):
        # поиск по имени в полном пути, начиная с начала (с корня)
        strF = '|'.join(set(map(lambda x: str(x), self.rules)))
        self._make_re(strF)


# ====== end name's filters

class fAbcRange(abcFilter):

    def _compile(self):
        opl = op.ge if self.left_margin else op.gt
        opr = op.le if self.right_margin else op.lt

        opf = op.not_ if self.color == filter_color.BLACK else op.truth
        self._check_func = lambda x: opf(opl(x, self.low_level) & opr(x, self.hight_level))

    def __init__(self, color=filter_color.WHITE,
                 low_level=None, high_level=None,
                 left_margin=True, right_margin=True):
        assert type(left_margin) == bool
        assert type(right_margin) == bool

        super().__init__(color=color)

        self._left_margin = left_margin
        self._right_margin = right_margin
        self._low_level = low_level
        self._hight_level = high_level

        self._compile()

    @property
    def low_level(self):
        return self._low_level

    @low_level.setter
    def low_date(self, value):
        self._low_level = value
        self._compile()

    @property
    def hight_level(self):
        return self._hight_level

    @hight_level.setter
    def hight_level(self, value):
        self._hight_date = value
        self._compile()

    @property
    def left_margin(self):
        return self._left_margin

    @left_margin.setter
    def left_margin(self, is_left_margin):
        assert type(is_left_margin) == bool
        self._left_margin = is_left_margin
        self._compile()

    @property
    def right_margin(self):
        return self._right_margin

    @right_margin.setter
    def right_margin(self, value):
        assert type(value) == bool
        self._right_margin = value
        self._compile()


# file size filters
class fFileSize(fAbcRange):

    def check(self, item):
        st = os.stat(item)
        x = st.st_size
        return self._check_func(x)

    def s_check(self, item):
        return self._check_func(item['size'])

    def __init__(self, color=filter_color.WHITE,
                 low_size=0, high_size=1e19,
                 left_margin=True, right_margin=True):
        super().__init__(color=color,
                         low_level=low_size, high_level=high_size,
                         left_margin=left_margin, right_margin=right_margin)

        self._type = filter_type.SIZE
        self._subtype = filter_subtype.SIZE_MARGIN

    @property
    def rules(self):
        return {'low_size': self.low_level, 'hight_size': self.hight_level,
                'left_margin': self.left_margin, 'right_margin': self.right_margin}


# ====== end file size filters
# file date change-create filters

class fFileDate(fAbcRange):

    def check(self, item):
        st = os.stat(item)
        x = dt.datetime.fromtimestamp(st.st_mtime).date()
        return self._check_func(x)

    def s_check(self, item):
        return self._check_func(item['mod_date'])

    def __init__(self, color=filter_color.WHITE,
                 low_date=None,
                 high_date=dt.datetime.now().date(),
                 left_margin=True, right_margin=True):
        # assert isinstance(low_date, dt.datetime)
        # assert isinstance(high_date, dt.datetime)

        super().__init__(color=color,
                         low_level=low_date or dt.date(year=1970, month=1, day=1),
                         high_level=high_date or dt.date(year=2270, month=1, day=1),
                         left_margin=left_margin, right_margin=right_margin)

        self._type = filter_type.DATE
        self._subtype = filter_subtype.DATE_MARGIN

    @property
    def low_date(self):
        return self.low_level

    @low_date.setter
    def low_date(self, ldate):
        assert type(ldate) == dt.date
        self.low_level = ldate or dt.date(year=1970, month=1, day=1)

    @property
    def hight_date(self):
        return self.hight_level

    @hight_date.setter
    def hight_date(self, hdate):
        assert type(hdate) == dt.date
        self.hight_level = hdate or dt.date(year=2270, month=1, day=1)

    @property
    def rules(self):
        return {'low_date': self.low_date.strftime('%Y-%m-%d'), 'hight_date': self.hight_date.strftime('%Y-%m-%d'),
                'left_margin': self.left_margin, 'right_margin': self.right_margin}


class fFileDateExact(abcFilter):

    def _compile(self):
        self._check_func = op.eq if self.color == filter_color.WHITE else op.ne

    def check(self, item):
        st = os.stat(item)
        x = dt.datetime.fromtimestamp(st.st_mtime).date()
        return self._check_func(x, self.check_date)

    def s_check(self, item):
        return self._check_func(item['mod_date'], self.check_date)

    def __init__(self, color=filter_color.WHITE, check_date=None):
        assert type(check_date) == dt.date

        super().__init__(color=color)

        self._type = filter_type.DATE
        self._subtype = filter_subtype.DATE_EXACT

        self._check_date = check_date
        self._compile()

    @property
    def check_date(self):
        return self._check_date

    @check_date.setter
    def check_date(self, cdate):
        assert type(cdate) == dt.date
        self._check_date = cdate

    @property
    def rules(self):
        return self.check_date.strftime('%Y-%m-%d')


# ====== end date's filters

# file attributes filters (windows)
class fArchAttrib(abcFilter):
    def add_rule(self):
        raise NotImplemented

    def __init__(self, color=filter_color.WHITE):
        super().__init__(color=color)
        self._type = filter_type.ATTRIB
        self._compile()

    def _compile(self):
        self._check_func = op.eq if self.color == filter_color.WHITE else op.ne

    def check(self, strPath):
        xr = subprocess.check_output(['attrib', strPath])
        try:
            return self._check_func(chr(xr[0]), 'A')
        except IndexError:
            return False

    def s_check(self, item):
        return item['isA']

    @property
    def rules(self):
        return 'A-attribute'


# ====== end attributes's filters

# def fdate():
#     # for i in lst_test:
#     #     st = os.stat(i)
#     #     print(i, st.st_size, dt.datetime.fromtimestamp(st.st_mtime))
#     fdt1 = fFileDate(color=filter_color.WHITE,
#                      low_date=dt.date(year=2020, month=1, day=1))
#
#     print(fdt1)
#     # print(fdt1.check(dt.date(year=2021, month=1, day=1)))
#     lt1 = list(filter(fdt1.check, lst_test))
#
#     for i in lt1:
#         st = os.stat(i)
#         print(i, dt.datetime.fromtimestamp(st.st_mtime).date())
#
#     print('*' * 50)
#
#     fdt2 = fFileDateExact(color=filter_color.WHITE, check_date=dt.date(year=2021, month=4, day=12))
#     print(fdt2)
#
#     lt2 = list(filter(fdt2.check, lst_test))
#     for i in lt2:
#         st = os.stat(i)
#         print(i, dt.datetime.fromtimestamp(st.st_mtime).date())
#     # print(fdt2.check(dt.datetime(year=2021, month=1, day=1)))
#
#
# def main():
#     fp1 = fFileName(rules=r'\w+', color=filter_color.BLACK, subtype=filter_subtype.EXT)
#     # fp1.add_rule('ipynb')
#     # fp1.add_rule('xls[xbm]?')
#     # fp1.add_rule(r'ipynb')
#
#     print(fp1._search)
#     lt = list(filter(fp1.check, lst_test))
#     for i in lt:
#         print(i)
#
#     # for i in lst_test:
#     #     print(i, fp1.check(i))
#
#     print('-' * 50)
#     fp2 = fDirName(rules=r'OSN-2020, \.', color=filter_color.WHITE)
#     print(fp2._search)
#
#     lt = list(filter(fp2.check, lst_test))
#     for i in lt:
#         print(i)
#
#     # for i in lst_test:
#     #     print(i, fp2.check(i))
#
#     print(fp1)
#     print(fp2)
#     print('main done')
#
#
# if __name__ == '__main__':
#     # main()
#     fdate()
#     print('All done.')
