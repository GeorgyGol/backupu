"""
Entry point for COPY//MOVE-commend
run from batch, do various files moving works
"""
from cmdl_backupu import actions, arg_parse  # , new_folder


def copyu():
    xpars = arg_parse.Params(work_type=actions.work_types.COPY)

    # str_comm = ['~s', '/home/egor/git/jupyter/housing_model',
    #             '~d', '/home/egor/T',
    #             '~n', 'test work',
    #             '~e', 'overwrite',
    #             '-e', 'pyc',
    #             '+e', 'py;sqlite? txt,ipynb',
    #             '-n', '_;~',
    #             '+n', 'year,month;serv',
    #             '~l', 'debug',
    #             '+d', '2020/01/01-2021/12/31']

    # for debug: get params from string
    # args = xpars.parse_args(args=str_comm)

    # get params from command string
    args = xpars.parse_args()
    smb_src = '/run/user/1000/gvfs/smb-share:server=commd.local,share=statistica'

    xCU = actions.xCopyU(source_base_dir=xpars.source,
                         log_level=xpars.log_level,
                         destination_base_dir=xpars.destination,
                         destination_subdir=xpars.name,
                         scan_filters=xpars.filters,
                         new_folder_rule=xpars.exist_destination,
                         archive_format=xpars.zip)

    # destination_subdir='BACKUP_{}'.format(dt.datetime.now().strftime('%d_%m_%Y')),

    xCU.run()

if __name__ == "__main__":
    # main()
    copyu()
    print('Copy4U done.')
