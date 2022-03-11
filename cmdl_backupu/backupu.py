"""
Entry point for BACKUP-commend
run from batch, do various backup works
"""

import logging
import re

from cmdl_backupu import actions, arg_parse


def main():
    def make_param_list(strParams):
        lst = list(map(str.strip, filter(None, re.split('[;,]', strParams))))
        return lst

    log_levels = {'critical': logging.CRITICAL, 'error': logging.ERROR, 'warn': logging.WARNING, 'info': logging.INFO,
                  'debug': logging.DEBUG, 'none': None}

    xpars = arg_parse.Params(work_type=actions.work_types.BACKUP)
    # args=parse_args()

    str_comm = ['~s', '/home/egor/git/jupyter/housing_model',
                '~d', '/home/egor/T', '~l', 'error', '~n', 'test work',
                '-e', 'pyc,xls?,py.*', '+e', 'py;sqlite? txt',
                '-f', r'\\PY\\', '+f', r'py\\',
                '-n', '_;~', '+n', 'test',
                '+d', '2020/01/01-2021/12/31']

    args = xpars.parse_args(args=str_comm)

    for arg in vars(args):
        print(arg, getattr(args, arg))

    print(xpars.zip)
    print(xpars.source)
    print(xpars.destination)
    print(xpars.log_level)
    print(xpars.name)
    print(xpars.backup_type)
    print(xpars.work_type)
    for f in xpars.filters:
        print(f)


if __name__ == "__main__":
    main()
    print('All done')
