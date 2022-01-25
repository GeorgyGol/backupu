from os import path, listdir
from pathlib import Path


class nameRule():
    def __init__(self, prefix='', name='', sufix='', format='', delimiter='_'):
        self._new_name = name
        self._delim = delimiter
        self._prefix = prefix
        self._sufix = sufix
        self._format = format

    @property
    def new_name(self):
        return self._new_name


class newFolder:

    def __init__(self, strBaseFolder, prefix='', sub_name='', sufix='', delimiter='_', format='', if_exsist='inc'):
        assert Path(strBaseFolder).exists()
        assert Path(strBaseFolder).is_dir()

        self._basePath = Path(strBaseFolder)
        self.rule(prefix=prefix, sub_name=sub_name, sufix=sufix, delimiter=delimiter, format=format)
        self._if_exsist = if_exsist

    def rule(self, prefix='', sub_name='', sufix='', delimiter='_', format=''):
        self._prefix = prefix
        self._sub_name = sub_name
        self._sufix = sufix
        self._delimiter = delimiter
        self._format = format

    def _construct_subpath(self):
        _dp = self._delimiter if self._prefix else ''
        _ds = self._delimiter if self._sufix else ''

        print(listdir(path.join(self._basePath)))

        return f'{self._prefix}{_dp}{self._sub_name}{_ds}{self._sufix}'

    def check_exists(self):
        new_path = path.join(self._basePath, self._construct_subpath())
        return Path(new_path).exists()

    @property
    def folder(self):
        if self._sub_name:
            return path.join(self._basePath, self._construct_subpath())
        else:
            return self._basePath

    @property
    def base_path(self):
        return self._basePath


def check_folder_class():
    fld = newFolder(path.join('/home', 'egor', 'git'), sub_name='test')
    print(fld.base_path)
    print(fld.check_exists())
    print(fld.folder)


if __name__ == '__main__':
    # check_folder_class()

    print('All done.')
