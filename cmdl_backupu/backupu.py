"""
Entry point for BACKUP-commend
run from batch, do various backup works
"""

import datetime as dt

from cmdl_backupu import actions, arg_parse, new_folder


def main():
    xpars = arg_parse.Params(work_type=actions.work_types.BACKUP)

    # str_comm = ['~s', '/home/egor/git/jupyter/housing_model',
    #             '~w', 'inc',
    #             '~d', '/home/egor/T',
    #             '~n', 'test work',
    #             '-e', 'pyc,xls?',
    #             '+e', 'py;sqlite? txt',
    #             '-n', '_;~',
    #             '+n', 'year,month,serv',
    #             '-a',
    #             '~l', 'info',
    #             '+d', '2020/01/01-2022/12/31']

    # for debug: get params from string
    # args = xpars.parse_args(args=str_comm)

    # get params from command string
    args = xpars.parse_args()
    xBU = actions.xBackupU(source_base_dir=xpars.source,
                           destination_base_dir=xpars.destination,
                           destination_subdir='BACKUP_{}'.format(dt.datetime.now().strftime('%d_%m_%Y')),
                           log_level=xpars.log_level,
                           backup_type=xpars.backup_type,
                           scan_filters=xpars.filters,
                           archive_format=xpars.zip,
                           prefix=xpars.backup_type.name,
                           use_A_atrib=xpars.a_attr,
                           new_folder_rule=new_folder.incRule())
    xBU.run()

if __name__ == "__main__":
    main()
    print('Backup4u done')
