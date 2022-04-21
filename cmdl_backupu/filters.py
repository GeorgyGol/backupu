"""
definitions for classes of filters for filtering scanned files list from class xScan (module scan this project)
all these classes is supposed to be used in the class xScan to filter the list obtained when scanning by
this class - a list of dictionaries with file attributes (name, full path, date, size, etc.)

    ONE RULE = ONE FILTER

    all filters based on abstract class abcFilter;
    filters can be BLACK, WHITE or RED:
        White means 'selected rules pass',
        Black means 'all but selected rules pass',
        Red means 'only selected rules pass' (strict White filter)

    WHITE filters applyes first, next BLACK, RED - last
    No filters means 'all files pass'

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
from enum import Enum  # , auto
from pathlib import Path


class filter_type(Enum):
    PATH = 1  # auto()
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
    RED = 3


class abcFilter(ABC):
    """  base class for all filters  """

    def __init__(self, color: filter_color = filter_color.WHITE):
        assert isinstance(color, filter_color)
        self._color = color

    @property
    def type(self) -> filter_type:
        return self._type

    @property
    def subtype(self) -> filter_subtype:
        return self._subtype

    @property
    def color(self) -> filter_color:
        return self._color

    @abstractmethod
    def _compile(self):
        """
        compile filter rule - commonly filter re-expression
        """
        pass

    @abstractmethod
    def check(self, item: str) -> bool:
        """
        function for make filtering - apply rule to item and return bool result filtering
        :param item:
        :return: filtering result
        """
        pass

    @abstractmethod
    def s_check(self, item: dict) -> bool:
        """
        function for make filtering - apply rule to item and return bool result filtering
        :param item: dict with file properties from xScan.scan()
        :return: filtering result
        """
        pass

    @property
    def rule(self):
        return self._rule

    def __str__(self):
        # for python 3.10 ->
        # return f'{self.color.name} filter on {self.type.name} ({self.subtype.name}); rule = {self.rule}'

        _s = '{color} filter on {type} ({subtype}); rule = {rule}'
        return _s.format(color=self.color.name, type=self.type.name,
                         subtype=self.subtype.name, rule=repr(self.rule))

    @property
    def BasePath(self) -> str:
        return self._base_path

    @BasePath.setter
    def BasePath(self, value: str):
        assert os.path.exists(value), 'Must get exisiting dir'
        self._base_path = value


# =================== file path-names filters - using re =============================

class filterFilePath(abcFilter):
    """
    class for filter on full file path, working on item['path'] scanned file list, for rule use re-expressions
    base class for filtering on name, dirs and extension classes
    """

    def __init__(self, color=filter_color.BLACK, case=string_case.STRICT, rule: str = '', strBasePath=''):
        """
        :param color: BLACK or WHITE for 'only but' or 'only' items
        :param case: case sensivity (key (?i) in re)
        :param rules: re-expression for filtering
        :param strBasePath: base file path from xScan class for exclude from re-search
        """
        assert isinstance(case, string_case)

        super().__init__(color=color)

        self._type = filter_type.PATH
        self._subtype = filter_subtype.NAME
        self._case = case
        self._base_path = strBasePath

        self._rule = rule
        self._str_pre = '(?i)' if self.case == string_case.ANY else ''

        self._search = None  # prepared and compiled re-object

        self._compile()

        if self.color == filter_color.BLACK:
            self._check_func = lambda item: self._search.search(self._path_transform(item)) is None
        else:
            self._check_func = lambda item: self._search.search(self._path_transform(item)) is not None

    def _path_transform(self, file_path):
        """
        for re-define in child classas - get some part from full file path for re-search (exclude base scan path)
        this function return param
        :param file_path: str - full file path
        :return: str - working part of full path
        """
        return file_path[len(self._base_path) + 1:]

    @property
    def case(self):
        """
        :return: filter case-sensivity
        """
        return self._case

    def __str__(self):
        # for Python 3.10 ->
        # return super().__str__() + f'; string case: {self.case.name}'
        _s = '; string case: {case}, exclude path {base_path}'
        return super().__str__() + _s.format(case=self.case.name, base_path=self.BasePath)

    def check(self, item):
        return self._check_func(item)

    def s_check(self, item):
        return self._check_func(item['path'])

    def _compile(self):
        strF = self._str_pre + self._rule
        self._search = re.compile(strF)
        return self._search


class filterFileName(filterFilePath):
    """
    class for filter on file name only
    """

    def __init__(self, color=filter_color.BLACK, case=string_case.STRICT, rule=''):
        super().__init__(color=color, case=case, rule=rule)

        self._type = filter_type.FILE
        self._subtype = filter_subtype.NAME

    def _path_transform(self, path_string: str) -> str:
        """
        get file name without extension from full path
        :param path_string: string - full file path
        :return: string - file name
        """
        # print(os.path.splitext(os.path.split(path_string)[-1])[0], Path(path_string).stem, Path(path_string).name)
        _x = Path(path_string).stem
        return Path(path_string).stem


class filterFileExt(filterFilePath):
    """
    class for filter on file extension only
    """

    def s_check(self, item):
        return self._check_func(item['ext'])

    def __init__(self, color=filter_color.BLACK, case=string_case.STRICT, rule=''):
        super().__init__(color=color, case=case, rule=rule)

        self._type = filter_type.FILE
        self._subtype = filter_subtype.EXT

        if self.color == filter_color.BLACK:
            self._check_func = lambda item: self._search.search(item) is None
        else:
            self._check_func = lambda item: self._search.search(item) is not None


class filterDirName(filterFilePath):
    """
    filter by file parent dir full path, exclude name and ext
    """

    def __init__(self, color=filter_color.BLACK,
                 case=string_case.STRICT, rule=''):
        super().__init__(color=color, case=case, rule=rule)
        self._subtype = filter_subtype.NAME
        self._type = filter_type.DIR

    def _path_transform(self, path_string: str) -> str:
        """
        get file path exclude name and ext
        :param path_string: string - full file path
        :return: string - file parent dir full path
        """
        return str(pathlib.Path(path_string).parent)[len(self.BasePath) + 1:]


# =================== end file path-names filters - using re =========================

# =================== file path-names filters - using re =============================
class fAbcRange(abcFilter):

    def _compile(self):
        if self.color in [filter_color.WHITE, filter_color.RED]:
            opl = op.ge if self.left_margin else op.gt
            opr = op.le if self.right_margin else op.lt
            self._check_func = lambda x: opl(x, self.low_level) & opr(x, self.hight_level)
        else:
            opl = op.le if self.left_margin else op.lt
            opr = op.ge if self.right_margin else op.gt
            self._check_func = lambda x: (opl(x, self.low_level) | opr(x, self.hight_level))

    def __init__(self, color: filter_color = filter_color.WHITE,
                 low_level: int = None, high_level: int = None,
                 left_margin: bool = True, right_margin: bool = True):
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
    def left_margin(self) -> bool:
        return self._left_margin

    @left_margin.setter
    def left_margin(self, is_left_margin: bool):
        assert type(is_left_margin) == bool
        self._left_margin = is_left_margin
        self._compile()

    @property
    def right_margin(self) -> bool:
        return self._right_margin

    @right_margin.setter
    def right_margin(self, value: bool):
        assert type(value) == bool
        self._right_margin = value
        self._compile()


# =================== file size filters (range, in bytes) =============================
class filterFileSize(fAbcRange):
    """
    filter for file size in bytes
    """

    def check(self, item) -> bool:
        st = os.stat(item)
        x = st.st_size
        return self._check_func(x)

    def s_check(self, item) -> bool:
        return self._check_func(item['size'])

    def __init__(self, color: filter_color = filter_color.WHITE,
                 low_level: int = 0, high_level: int = 1e19,
                 left_margin: bool = True, right_margin: bool = True):
        """
        for WHITE filter:
            self.low_level > file_size > self.hight_level
                for self.left_margin = self.right_margin = True
            self.low_level >= file_size >= self.hight_level

        for BLACK filter:
            self.low_level < file_size OR file_size > self.hight_level
                for self.left_margin = self.right_margin = True
            self.low_level <= file_size OR file_size >= self.hight_level

        :param color: BLACK or WHITE filter
        :param low_level:
        :param high_level: default set very big num for filtering low_size > file_size > Infinity
        :param left_margin: if True -  low_size >= file_size > high_size, if False - low_size > file_size > high_size
        :param right_margin: if True -  low_size < file_size >= high_size, if False - low_size > file_size > high_size
        """
        super().__init__(color=color,
                         low_level=low_level, high_level=high_level,
                         left_margin=left_margin, right_margin=right_margin)

        self._type = filter_type.SIZE
        self._subtype = filter_subtype.SIZE_MARGIN

    @property
    def rule(self):
        return {'low_level': self.low_level, 'hight_level': self.hight_level,
                'left_margin': self.left_margin, 'right_margin': self.right_margin}


# =================== end file size filters (range, in bytes) =============================

# file date change-create filters

class filterFileDateRange(fAbcRange):
    """
    filter for file change datetime
    """

    def check(self, item) -> bool:
        st = os.stat(item)
        x = dt.datetime.fromtimestamp(st.st_mtime)
        return self._check_func(x)

    def s_check(self, item) -> bool:
        return self._check_func(item['change_date'])

    def __init__(self, color: filter_color = filter_color.WHITE,
                 low_date=dt.datetime(year=1970, month=1, day=1),
                 high_date=dt.datetime.now(),
                 left_margin=True, right_margin=True):
        assert isinstance(low_date, dt.date) or isinstance(low_date, dt.datetime)
        assert isinstance(high_date, dt.date) or isinstance(low_date, dt.datetime)

        super().__init__(color=color,
                         low_level=low_date or dt.date(year=1970, month=1, day=1),
                         high_level=high_date,
                         left_margin=left_margin, right_margin=right_margin)

        self._type = filter_type.DATE
        self._subtype = filter_subtype.DATE_MARGIN
        self._compile()

    @property
    def low_date(self):
        return self.low_level

    @low_date.setter
    def low_date(self, ldate):
        assert isinstance(ldate, dt.date) or isinstance(ldate, dt.datetime)
        self.low_level = ldate
        self._compile()

    @property
    def hight_date(self):
        return self.hight_level

    @hight_date.setter
    def hight_date(self, hdate):
        assert isinstance(hdate, dt.date) or isinstance(hdate, dt.datetime)

        self.hight_level = hdate
        self._compile()

    @property
    def rule(self):
        return {'low_date': self.low_date.strftime('%Y-%m-%d %H:%M'),
                'hight_date': self.hight_date.strftime('%Y-%m-%d %H:%M'),
                'left_margin': self.left_margin, 'right_margin': self.right_margin}


class filterFileDateExact(filterFileDateRange):
    """
    filter of file change date exactly
    """

    def _compile(self):
        if self.color in [filter_color.WHITE, filter_color.RED]:
            self._check_func = lambda x: x == self.hight_date
        else:
            self._check_func = lambda x: x != self.hight_date

    def __init__(self, color=filter_color.WHITE,
                 file_date=dt.datetime.now().date()):
        assert isinstance(file_date, dt.date) or isinstance(file_date, dt.datetime)

        super().__init__(color=color,
                         low_date=dt.date(year=1970, month=1, day=1),
                         high_date=file_date)

        self._subtype = filter_subtype.DATE_EXACT

    @property
    def file_date(self):
        return super().hight_level

    @file_date.setter
    def file_date(self, hdate):
        super().hight_level = hdate

    @property
    def rule(self):
        return {'change_date': self.hight_date.strftime('%Y-%m-%d')}


# ====== end date's filters

# =================== file attributes filters (windows, A-attr) =============================

class filterArchAttrib(abcFilter):
    """
    filter for archive file attribute - WORK ONLY FOR Windows OS!
    for linux return actual a-atrib value (False for WHITE and True for BLACK - a-atrib not setting up)
    """

    def __init__(self, color: filter_color = filter_color.WHITE):
        super().__init__(color=color)
        self._type = filter_type.ATTRIB
        self._compile()

    def _compile(self):
        self._check_func = op.eq if self.color in [filter_color.WHITE, filter_color.RED] else op.ne

    def check(self, strPath: str) -> bool:
        xr = subprocess.check_output(['attrib', strPath])
        try:
            return self._check_func(chr(xr[0]), 'A')
        except IndexError:
            return False

    def s_check(self, item):
        _d = {filter_color.WHITE: item['A-attr'],
              filter_color.BLACK: not item['A-attr'],
              filter_color.RED: item['A-attr']}
        return _d[self.color]

    @property
    def rule(self):
        return 'A-attribute'

    def __str__(self):
        # for python 3.10 ->
        # return f'{self.color.name} filter on {self.type.name} ({self.subtype.name}); rule = {self.rule}'

        _s = '{color} filter on {type}; rule = {rule}'
        return _s.format(color=self.color.name, type=self.type.name, rule=self.rule)

# =================== end file attributes filters (windows, A-attr) =============================
