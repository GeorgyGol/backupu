"""
Entry point for BACKUP-commend
run from batch, do various backup works
"""

import argparse
import logging
import os.path
import re

from cmdl_backpz import scan, actions, __version__


def parse_args():
    parser = argparse.ArgumentParser(description='Backup (full, inc or diff) and copy files from SOURCE to DESTINATION',
                                     prog='backupz.py',
                                     epilog="(c) CMASF, g.golyshev@forecast.ru", fromfile_prefix_chars='@', prefix_chars='-+/')
    parser.add_argument('/n', '--name', help='name for work', required=False, default='backup_work')
    parser.add_argument('/s', '--source', help='Source dir (one) for backup or copy', required=True)
    parser.add_argument('/d', '--destination', help='Target dir (one) for backup or copy', required=True)
    parser.add_argument('/z', '--zip', help='ZIP-Archive destination', required=False, action='store_true')
    parser.add_argument('/w', '--work', help='backup (full, inc or diff) or copy', default=actions.WORK_TYPE.copy,
                        choices=[' {}'.format(actions.WORK_TYPE.backup_full),
                                 ' {}'.format(actions.WORK_TYPE.backup_inc),
                                 ' {}'.format(actions.WORK_TYPE.backup_diff),
                                 ' {}'.format(actions.WORK_TYPE.copy)])
    parser.add_argument('/l', '--log_level', help='log with log-level or none', default='info',
                        choices=[' info', ' debug', ' error', ' none', ' warn', ' critical'])
    parser.add_argument('-e', '--exclude-extensions', help='black list: exclude files with these extensions, separated by comma')
    parser.add_argument('+e', '--only-extensions',
                        help='white list: work only with files with these extensions, separated by comma')
    parser.add_argument('-f', '--exclude-folders',
                        help='black list: exclude these folders, separated by comma')
    parser.add_argument('+f', '--only-folders',
                        help='white list: work only with these folder and included in')
    parser.add_argument('-n', '--exclude-names',
                        help='black list: exclude files with these names, separated by comma (using re.search')
    parser.add_argument('+n', '--only-names',
                        help='white list: work only with files with these names, separated by comma (using re.search')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))

    parser.epilog='for work parameters from file use: backupz @<filename>'
    #args=parser.parse_args([r'-s \\Commd\P_CMASFProject', r'-d d:\p', '-z', '-e tmp xml csv', '-f @Recycle', '-n \~\$'])
    # args = parser.parse_args(['<backup-args1.txt']) # for args from file

    #args = parser.parse_args(['--version'])
    return parser.parse_args()

def main():

    def make_param_list(strParams):
        lst=list(map(str.strip, filter(None, re.split('[;,]', strParams))))
        return lst

    log_levels={'critical':logging.CRITICAL, 'error':logging.ERROR, 'warn':logging.WARNING, 'info':logging.INFO,
                'debug':logging.DEBUG, 'none':None}

    args=parse_args()
    # for arg in vars(args):
    #     print(arg, getattr(args, arg))

    name=args.name
    source=args.source.strip()
    dest=os.path.normpath(args.destination.strip())
    z=args.zip
    w=args.work.strip()

    log_level=args.log_level.lower().strip()

    filters=[]
    if args.exclude_extensions:
        filters.append(scan.x_extension_list(name='excl. ext', lst_ext=make_param_list(args.exclude_extensions)))
    if args.only_extensions:
        filters.append(scan.x_extension_list(name='only ext', lst_ext=make_param_list(args.only_extensions)), black=False)

    if args.exclude_folders:
        filters.append(scan.x_folders(name='excl. dirs', lst_folders=make_param_list(args.exclude_folders)))
    if args.only_folders:
        filters.append(scan.x_folders(name='only dirs', lst_folders=make_param_list(args.only_folders)), black=False)

    if args.exclude_names:
        filters.append(scan.x_names(name='excl. names', lst_names=make_param_list(args.exclude_names)))
    if args.only_names:
        filters.append(scan.x_names(name='excl. names', lst_names=make_param_list(args.only_names)), black=False)

    x = actions.XBackup_A(strWorkPath=source, name=name, strSavePath=dest)
    x.filters(*filters)

    x.backup(work_type=w, zip=z, log_level=log_levels[log_level])

    # if w==actions.WORK_TYPE.copy:
    #     x.path_rule = actions.x_path_copy(x.save_path)
    #     x.copy(zip=z, log_level=log_levels[log_level])
    # else:
    #     x.path_rule = actions.x_path_date_inc(dest, prefix='INC', month_format='%b')
    #     x.backup(work_type=w, zip=z, log_level=log_levels[log_level])




if __name__ == "__main__":
    main()
    print('All done')

