import logging
import sys

import pandas as pd

from cmdl_backupu.actions import file_size2mb
from cmdl_backupu.filters import *
from cmdl_backupu.scan import xScan


class abcActionOnSource(ABC):

    def __init__(self, source_base_dir: str, log_level=logging.DEBUG,
                 scan_filters: list = list(), log_file='') -> None:
        assert Path(source_base_dir).exists(), 'source dir must exists'
        self._source = source_base_dir

        self._scan = xScan(start_path=self.source_folder)
        self._scan.set_filters(*scan_filters)

        self._log_level = log_level
        self._setup_logger(log_file_name=log_file)
        self._post_work_action = lambda x: x
        super().__init__()

    def _setup_logger(self, log_file_name):
        self._log = logging.getLogger('console')

        if log_file_name:
            logfile = log_file_name
            fl = logging.FileHandler(logfile, mode='a')
            fl.setLevel(logging.INFO)
            self._log.addHandler(fl)

        self._log.setLevel(self._log_level)
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(self._log_level)
        self._log.addHandler(ch)

        self._log.info(
            '{dt} : INFO work'.format(dt=dt.datetime.now().strftime('%Y-%m-%d %H:%M')))
        self._log.info('SOURCE : {}'.format(str(self.source_folder)))
        self._log.info('')
        self._log.info('SCAN FILTERS   :')
        for f in self._scan.filters:
            self._log.info(f)
        self._log.info('=' * 100)

        return self._log

    @property
    def source_folder(self):
        return self._source

    def _do_scan(self) -> list:
        self._scan.scan()
        self._log.info('scan source done')

        self._ffiles = self._scan.files(filtered=True)
        self._files = self._scan.files(filtered=False)
        _cnt_files = len(self._ffiles)

        self._log.info('files in source {all_files} : after filters select {f_files} files'.format(
            all_files=self._scan.size(filtered=False), f_files=_cnt_files))

        all_weight = file_size2mb(sum([f['size'] for f in self._files]))
        flt_weight = file_size2mb(sum([f['size'] for f in self._ffiles]))

        self._log.info('size in source {all_files} (Mb) : filtered size {f_files} (Mb)'.format(
            all_files=all_weight, f_files=flt_weight))

        return self._ffiles

    @abstractmethod
    def run(self, do_action=True, do_create_dest_tree=True):
        pass


class xInfoU(abcActionOnSource):

    def run(self, do_action=True, do_create_dest_tree=True):
        self._do_scan()

        f_filtered = self._ffiles
        f_unf = self._files

        return f_filtered

    def __init__(self, source_base_dir: str, log_level=logging.DEBUG, scan_filters: list = list()) -> None:
        super().__init__(source_base_dir=source_base_dir, log_level=log_level, scan_filters=scan_filters)


if __name__ == '__main__':
    smb_src = '/run/user/1000/gvfs/smb-share:server=commd.local,share=personal/Golyshev'

    filters = [filterFileExt(color=filter_color.WHITE, rule=r'txt\b'),
               filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileName(color=filter_color.WHITE, rule=r'Голышев'),
               filterFileExt(color=filter_color.WHITE, rule=r'pdf'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb'),
               ]
    xi = xInfoU(source_base_dir=smb_src, log_level=logging.INFO,
                scan_filters=filters)
    pdf = pd.DataFrame(xi.run())
    print('=' * 100)
    for i, v in pdf.iterrows():
        print(v['name'], v['ext'])
