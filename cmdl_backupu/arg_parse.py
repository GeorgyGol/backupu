import argparse
import datetime as dt
import logging
import re
from pathlib import Path

from cmdl_backupu import actions, filters, __version__, new_folder


class Params:
    bu_prog = 'backupu.py'
    cp_prog = 'copyu.py'
    inf_prog = 'infou.py'

    def __init__(self, work_type=actions.work_types.BACKUP) -> None:
        if work_type == actions.work_types.BACKUP:
            _sdescr = 'Backup files (full or incremental) from SOURCE to DESTINATION'
            self._prog_name = self.bu_prog  # 'backupu.py'
        elif work_type == actions.work_types.COPY:
            _sdescr = 'Copy files from SOURCE to DESTINATION'
            self._prog_name = self.cp_prog
        else:
            _sdescr = 'Get SOURCE file info'
            self._prog_name = self.inf_prog

        self._parser = argparse.ArgumentParser(description=_sdescr, prog=self._prog_name,
                                               epilog="Georgy Golyshev, g.golyshev@gmail.com",
                                               fromfile_prefix_chars='@', prefix_chars='-+$&~')
        self._parser.add_argument('~n', '--name', help='name for work', required=False, default='backup')
        self._parser.add_argument('~s', '--source', help='Source dir (one) - required', required=True)

        if work_type != actions.work_types.INFO:
            self._parser.add_argument('~d', '--destination', help='Target dir (one) for backup or copy', required=True)
            self._parser.add_argument('+z', '--zip', help='ZIP-Archive destination',
                                      required=False, action='store_true')
        else:
            self._parser.add_argument('~d', '--destination', help='Not used - for compability purpose',
                                      required=False)
            self._parser.add_argument('~w', '--work', help='Not used - for compability',
                                      default='FULL',
                                      choices=['FULL', 'INC', 'full', 'inc'])
            self._parser.add_argument('-a', '--not-archive', action='store_true',
                                      help='Not used - for compability')
            self._parser.add_argument('+z', '--zip', help='ZIP-Archive destination',
                                      required=False, action='store_true')
            self._parser.add_argument('~e', '--exist_dest', help='Not used - for compability',
                                      default='new',
                                      choices=['new', 'overwrite', 'error'])

        if work_type == actions.work_types.BACKUP:
            self._parser.add_argument('~w', '--work', help='backup full or inc',
                                      default='FULL',
                                      choices=['FULL', 'INC', 'full', 'inc'])
            self._parser.add_argument('-a', '--not-archive', action='store_true',
                                      help="""don't use file archive-attribute for backup - use date of last backup
                                       insteed. Work only on Windows, on Linux always use files date""")
        if work_type == actions.work_types.COPY:
            self._parser.add_argument('~e', '--exist_desc', help='If destination alredy exists do...',
                                      default='new',
                                      choices=['new', 'overwrite', 'error'])

        self._parser.add_argument('~l', '--log_level', help='log with log-level or none', default='info',
                                  choices=['info', 'debug', 'error', 'none', 'warn', 'critical'])
        self._parser.add_argument('-e', '--exclude-extensions',
                                  help='black list: exclude files with these extensions, separated by comma')
        self._parser.add_argument('+e', '--include-extensions',
                                  help='white list: work only with files with these extensions, separated by comma')
        self._parser.add_argument('-f', '--exclude-folders',
                                  help='black list: exclude these folders, separated by comma')
        self._parser.add_argument('+f', '--include-folders',
                                  help='white list: work only with these folder and included in')
        self._parser.add_argument('-n', '--exclude-names',
                                  help='black list: exclude files with these names, separated by comma')
        self._parser.add_argument('+n', '--include-names',
                                  help='white list: work only with files with these names, separated by comma')

        self._parser.add_argument('-d', '--exclude-dates',
                                  help='Black filter - date (last modification) range <YYYY/mm/dd-YYYY/mm/dd>, if high date omited - use now')
        self._parser.add_argument('+d', '--include-dates',
                                  help='White filter - date (last modification) range <YYYY/mm/dd-YYYY/mm/dd>, if high date omited - use now')

        self._parser.add_argument('-s', '--exclude-size',
                                  help='Black filter - size (in mBt) range <0-1e3>, if high level omited - extra large')
        self._parser.add_argument('+s', '--include-size',
                                  help='White filter - size (in mBt) range <0-1e3>, if high level omited - extra large')

        self._parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))

        self._parser.epilog = 'for work parameters from file use: <prog> @<filename>'.format(prog=self._prog_name)

    def parse_args(self, args=None):
        self._args = self._parser.parse_args(args=args)
        return self._args

    @property
    def zip(self):
        return vars(self._args)['zip']

    @property
    def a_attr(self):
        return not vars(self._args)['not_archive']

    @property
    def source(self):
        if Path(vars(self._args)['source']).exists():
            return vars(self._args)['source']
        else:
            raise FileNotFoundError('path {} not exist'.format(vars(self._args)['source']))

    @property
    def destination(self):
        return vars(self._args)['destination']

    @property
    def exist_destination(self):
        ret = {'new': new_folder.incRule(), 'overwrite': new_folder.exsistOKRule(), 'error': new_folder.errorRule()}
        return ret[vars(self._args)['exist_desc'].strip().lower()]

    @property
    def name(self):
        return vars(self._args)['name']

    @property
    def log_level(self):
        _ret = {'info': logging.INFO, 'debug': logging.DEBUG, 'error': logging.ERROR,
                'critical': logging.CRITICAL, 'none': logging.NOTSET, 'warn': logging.WARNING}
        _x = _ret[vars(self._args)['log_level'].lower()]
        return _x

    @property
    def backup_type(self):
        if self._prog_name == self.bu_prog:
            _tmp = {'FULL': actions.backup_types.FULL, 'INC': actions.backup_types.INC}
            return _tmp[vars(self._args)['work'].upper()]
        else:
            return ''

    @property
    def work_type(self):
        _tmp = {self.bu_prog: 'BACKUP', self.inf_prog: 'INFO', self.cp_prog: 'COPY'}
        return _tmp[self._prog_name]

    @property
    def filters(self):
        def initF(filterType=None, rules='', color=filters.filter_color.BLACK):
            re_delimit = re.compile('[,; ]+')
            try:
                rule_list = re_delimit.split(vars(self._args)[rules])
                return [filterType(color=color, rule=r) for r in rule_list]
            except:
                return list()

        def initFDt(rules='', color=filters.filter_color.BLACK):
            try:
                dtbl = [dt.datetime.strptime(d, '%Y/%m/%d') for d in vars(self._args)[rules].split('-')]
                if len(dtbl) == 1:
                    dtbl.append(dt.datetime.now())

                _tmp = filters.filterFileDateRange(color=color,
                                                   low_date=dtbl[0], high_date=dtbl[1])
                return [_tmp, ]
            except:
                return list()

        def initSizeRange(rules='', color=filters.filter_color.BLACK):
            try:
                dtbl = [float(d) for d in vars(self._args)[rules].split('-')]
                if len(dtbl) == 1:
                    dtbl.append(1e99)

                _tmp = filters.filterFileSize(color=color, low_level=dtbl[0], high_level=dtbl[1])
                return [_tmp, ]
            except:
                return list()

        ext_black = initF(filterType=filters.filterFileExt,
                          rules='exclude_extensions', color=filters.filter_color.BLACK)
        ext_white = initF(filterType=filters.filterFileExt,
                          rules='include_extensions', color=filters.filter_color.WHITE)
        path_black = initF(filterType=filters.filterFilePath,
                           rules='exclude_folders', color=filters.filter_color.BLACK)
        path_white = initF(filterType=filters.filterFilePath,
                           rules='include_folders', color=filters.filter_color.WHITE)
        name_black = initF(filterType=filters.filterFileName,
                           rules='exclude_names', color=filters.filter_color.BLACK)
        name_white = initF(filterType=filters.filterFileName,
                           rules='include_names', color=filters.filter_color.WHITE)

        dt_black = initFDt(rules='exclude_dates', color=filters.filter_color.BLACK)
        dt_white = initFDt(rules='include_dates', color=filters.filter_color.WHITE)

        sz_black = initSizeRange(rules='exclude_size', color=filters.filter_color.BLACK)
        sz_white = initSizeRange(rules='include_size', color=filters.filter_color.WHITE)

        return ext_black + ext_white + path_black + path_white + name_black + name_white + dt_black + dt_white + sz_black + sz_white



def main():
    xpars = Params(work_type=actions.work_types.BACKUP)
    # args=parse_args()

    str_comm = ['~s', '/home/egor/git/jupyter/housing_model',
                '~d', '/home/egor/T',
                '~l', 'error',
                # '~e', 'overwrite',
                '~w', 'full',
                '~n', 'test work',
                '~l', 'info',
                '-e', 'pyc,xls?,py.*',
                '+e', 'py;sqlite? txt',
                '-f', r'\\PY\\',
                '+f', r'py\\',
                '-n', '_;~',
                '+n', 'test',
                '+d', '2020/01/01-2021/12/31']

    args = xpars.parse_args(args=str_comm)

    for arg in vars(args):
        print(arg, getattr(args, arg))

    print(xpars.zip)
    # print(xpars.a_attr)
    # print(xpars.exist_destination)
    print(xpars.backup_type)
    print(xpars.source)
    print(xpars.destination)
    print(xpars.log_level)
    print(xpars.name)
    print('backup type', xpars.backup_type)
    print(xpars.work_type)
    for f in xpars.filters:
        print(f)


if __name__ == "__main__":
    main()
    print('All done')
