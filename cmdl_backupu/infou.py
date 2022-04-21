from cmdl_backupu import actions, arg_parse  # , new_folder


# import pandas as pd
# from io import StringIO

def infou():
    xpars = arg_parse.Params(work_type=actions.work_types.INFO)

    # str_comm = ['~s', '/home/egor/git/jupyter/housing_model',
    #             '~d', '/home/egor/T',
    #             '~n', 'test work',
    #             '~e', 'overwrite',
    #             '-e', 'pyc,xls?,py.*',
    #             '+e', 'py;sqlite? txt',
    #             '-f', '\.git',
    #             # '+f', r'py\\',
    #             '-n', '_;~',
    #             '+n', 'year$',
    #             '~l', 'info',
    #             '+d', '2020/01/01-2021/12/31']

    # ~s="/home/egor/git/jupyter/housing_model" ~d="/home/egor/T" ~n="test work" ~e="overwrite" -e="pyc,xls? py.*" +e="py;sqlite? txt" -f="\.git" -n="_;~" +n="year$" ~l="info" +d="2020/01/01-2021/12/31"

    # @/home/egor/PycharmProjects/backupu/param_works/house_model.params

    # for debug: get params from string
    # args = xpars.parse_args(args=str_comm)

    # get params from command string
    args = xpars.parse_args()

    xIF = actions.xInfoU(source_base_dir=xpars.source,
                         log_level=xpars.log_level,
                         scan_filters=xpars.filters)

    # destination_subdir='BACKUP_{}'.format(dt.datetime.now().strftime('%d_%m_%Y')),

    files = xIF.run()
    # pdf = pd.read_csv(StringIO('\n'.join(files)), sep=';')
    # print(pdf)
    # print('f'*50)
    # print(pdf[pdf['name']=='year'])
    for f in files:
        print(f)


if __name__ == "__main__":
    infou()
    print('InfoU done.')
