import datetime as dt
import operator as op
import os
import pathlib
import re
import subprocess
from abc import ABC, abstractmethod
from enum import Enum, auto

class filter_type(Enum):
    PATH = auto()
    DIR = auto()
    FILE = auto()
    ATTRIB = auto()
    DATE = auto()
    SIZE = auto()


class filter_subtype(Enum):
    NAME = auto()
    EXT = auto()
    DATE_MARGIN = auto()
    SIZE_MARGIN = auto()
    DATE_EXACT = auto()


class string_case(Enum):
    STRICT = auto()
    ANY = auto()


class filter_color(Enum):
    WHITE = auto()
    BLACK = auto()


class abcFilter(ABC):

    def __init__(self, color=filter_color.WHITE):
        assert isinstance(color, filter_color)
        self._color = color

    @property
    def type(self):
        return self._type

    @property
    def subtype(self):
        return self._subtype

    @property
    def color(self):
        return self._color

    @abstractmethod
    def _compile(self):
        pass

    @abstractmethod
    def check(self, item):
        pass

    @abstractmethod
    def s_check(self, item):
        pass

    @property
    def rules(self):
        return self._rules

    def __str__(self):
        return f'{self.color.name} filter on {self.type.name} ({self.subtype.name}); rules = {self.rules}'


# file path-names filters - using re
class fFilePath(abcFilter):

    def __init__(self, color=filter_color.BLACK, subtype=filter_subtype.EXT,
                 case=string_case.STRICT, rules=set()):
        assert isinstance(subtype, filter_subtype)
        assert isinstance(case, string_case)

        super().__init__(color=color)

        self._type = filter_type.PATH
        self._subtype = subtype
        self._case = case

        if isinstance(rules, str):
            self._rules = set(filter(lambda x: x != '', re.split(r'[ ,;]+', rules)))
        else:
            self._rules = set(rules)

        if self.case == string_case.ANY:
            self._rules = set(map(str.lower, self._rules))

        self._compile()

    @property
    def case(self):
        return self._case

    def __str__(self):
        return super().__str__() + f'; string case: {self.case.name}'

    def add_rule(self, rule):
        self._rules.add(rule)
        self._compile()

    def check(self, item):
        return self._check_func(item)

    def s_check(self, item):
        return self._check_func(item['path'])

    def _make_re(self, strRE):
        if self.case == string_case.ANY:
            str_pre = '(?i)'
        else:
            str_pre = ''

        strF = str_pre + strRE
        self._search = re.compile(strF)
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
            strF = '\.' + '|'.join(set(map(lambda x: f'({x})', self.rules))) + '$'
            self._make_re(strF)
        else:  # self.subtype == filter_subtype.NAME:
            # поиск по именам файлов
            strF = '|'.join(set(map(lambda x: f'({x})', self.rules)))
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
        strF = '|'.join(set(map(lambda x: f'({x})', self.rules)))
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


lst_test = ['/home/egor/git/jupyter/geckodriver.log',
            '/home/egor/git/jupyter/housing_model16072021.zip',
            '/home/egor/git/jupyter/ghostdriver.log',
            '/home/egor/git/jupyter/housing_model.zip',
            '/home/egor/git/jupyter/inn_1.txt',
            '/home/egor/git/jupyter/Rosstat.ipynb',
            '/home/egor/git/jupyter/employed_pers_pars/osn-11-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/osn-12-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/output20.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/output08_20.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/Без названия1.ipynb',
            '/home/egor/git/jupyter/employed_pers_pars/output07_20.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/output21.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/output20_1.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/output18.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/output19.xlsx',
            '/home/egor/git/jupyter/employed_pers_pars/Без названия.ipynb',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-10-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-11-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-12-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-08-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-04-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/Новости статистики Росстат перешел на 2018 базисный год.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-02-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-09-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/О международных сопоставлениях ВВП за 2014 год.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-07-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-05-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-03-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-06-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/OSN-2020/osn-01-2020.pdf',
            '/home/egor/git/jupyter/employed_pers_pars/.ipynb_checkpoints/Без названия1-checkpoint.ipynb',
            "/home/egor/git/jupyter/employed_pers_pars/.ipynb_checkpoints/Без названия-checkpoint.ipynb",
            '/home/egor/git/jupyter/HT/Data_ru/Р-1/Р-14.txt',
            '/home/egor/git/jupyter/HT/Data_ru/Р-1/Р-1-1.txt',
            '/home/egor/git/jupyter/HT/Data_ru/Р-1/Р-1-8.txt',
            '/home/egor/git/jupyter/HT/Data_ru/Р-1/Р-1-4.txt',
            '/home/egor/git/jupyter/HT/Data_ru/Р-1/Р-18.txt',
            '/home/egor/git/jupyter/HT/Data_ru/Р-1/Р-12.txt',
            '/home/egor/git/jupyter/rf-stat-build&modern-xml/.git/COMMIT_EDITMSG',
            '/home/egor/git/jupyter/rf-stat-build&modern-xml/.git/logs/HEAD',
            '/home/egor/git/jupyter/rf-stat-build&modern-xml/.git/logs/refs/heads/master',
            '/home/egor/git/jupyter/rf-stat-build&modern-xml/.git/objects/ea/6f66620412046c6eab99ff662f41e977e74767',
            '/home/egor/git/jupyter/rf-stat-build&modern-xml/.git/objects/46/2de57cd3f2bc95a4f02c3679070ce975b96fd6',
            '/home/egor/git/jupyter/rf-stat-build&modern-xml/.git/objects/b9/e714f98f57258ef608f3f56d1ec2307db0c4f6',
            '/home/egor/git/jupyter/CorrBanks/Base/step/jur_corr.csv',
            '/home/egor/git/jupyter/CorrBanks/Base/step/cenbum_corr.csv',
            '/home/egor/git/jupyter/CorrBanks/Base/step/banki.xlsb',
            '/home/egor/git/jupyter/CorrBanks/Base/step/banki.xlsx',
            '/home/egor/git/jupyter/CorrBanks/Base/step/pmbk_corr.csv',
            '/home/egor/git/jupyter/CorrBanks/Base/step/banki.xls']


def fdate():
    # for i in lst_test:
    #     st = os.stat(i)
    #     print(i, st.st_size, dt.datetime.fromtimestamp(st.st_mtime))
    fdt1 = fFileDate(color=filter_color.WHITE,
                     low_date=dt.date(year=2020, month=1, day=1))

    print(fdt1)
    # print(fdt1.check(dt.date(year=2021, month=1, day=1)))
    lt1 = list(filter(fdt1.check, lst_test))

    for i in lt1:
        st = os.stat(i)
        print(i, dt.datetime.fromtimestamp(st.st_mtime).date())

    print('*' * 50)

    fdt2 = fFileDateExact(color=filter_color.WHITE, check_date=dt.date(year=2021, month=4, day=12))
    print(fdt2)

    lt2 = list(filter(fdt2.check, lst_test))
    for i in lt2:
        st = os.stat(i)
        print(i, dt.datetime.fromtimestamp(st.st_mtime).date())
    # print(fdt2.check(dt.datetime(year=2021, month=1, day=1)))


def main():
    fp1 = fFileName(rules=r'\w+', color=filter_color.BLACK, subtype=filter_subtype.EXT)
    # fp1.add_rule('ipynb')
    # fp1.add_rule('xls[xbm]?')
    # fp1.add_rule(r'ipynb')

    print(fp1._search)
    lt = list(filter(fp1.check, lst_test))
    for i in lt:
        print(i)

    # for i in lst_test:
    #     print(i, fp1.check(i))

    print('-' * 50)
    fp2 = fDirName(rules=r'OSN-2020, \.', color=filter_color.WHITE)
    print(fp2._search)

    lt = list(filter(fp2.check, lst_test))
    for i in lt:
        print(i)

    # for i in lst_test:
    #     print(i, fp2.check(i))

    print(fp1)
    print(fp2)
    print('main done')


if __name__ == '__main__':
    # main()
    fdate()
    print('All done.')
