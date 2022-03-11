"""
Actions (copy, backup) for Google Claud Storage
destinations - storage bucket, source - local file system
"""
from google.cloud import storage

from cmdl_backupu.actions import *


def gc_storage_connect(path_json_key):
    client = storage.Client.from_service_account_json(path_json_key)
    # buckets = client.list_buckets()
    #
    # for bucket in buckets:
    #     print(bucket.name)
    return client


def dc_storage_bucket(client, bucket_name):
    return client.get_bucket(bucket_name)


class xCopyGCS(xCopyU):
    """
    copy files to google cloud storage bucket
    Example:

    filters = [filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb')] # any filters


    folder_name = 'CPYTST_{}'.format(dt.datetime.now().strftime('%d_%m_%Y'))
    source_path = '<some valid exists path>'

    path_key = <path to json google key file>
    client = gc_storage_connect(path_key)
    bsk = dc_storage_bucket(client, '<bucket name>')

    cw = xCopyGCS(source_base_dir=source_path, log_level=logging.INFO,
                  google_bucket=bsk, log_file_path=Path('../LOG/gcs_log.log'),
                  google_cloud_bucket_folder=folder_name, scan_filters=filters)

    cw.run()
    """

    def __init__(self, source_base_dir: str = '',
                 google_bucket: storage.Bucket = None, google_cloud_bucket_folder: str = '',
                 log_level=logging.DEBUG, scan_filters: list = list(),
                 log_file_path: str = '', set_up_logger_on_init=True) -> None:
        """
        :param source_base_dir: str or pathlike - path to source dir
        :param google_bucket: google.storage.Bucket - google bucket object
        :param google_cloud_bucket_folder: str - folder in given bucket
        :param log_level: logging level (in log-file log_level always = logging.INFO)
        :param scan_filters: list of abcFilter instances - filter for select source files
        :param log_file_path: path to log-file. In this class there is no destination folder, and log-file don't create automatcaly, so you must set path to it
        """

        assert Path(source_base_dir).exists(), 'source dir must exists'
        assert google_bucket is not None
        assert isinstance(google_bucket, storage.Bucket)

        self._work_name = 'COPY to GOOGLE CLOUD STORAGE, (bucket - "{}")'.format(google_bucket.name)
        self._archive_format = ''

        self._gcs_bucket = google_bucket
        self._source = source_base_dir
        self._dest_base = google_bucket.name

        self._scan = xScan(start_path=self.source_folder)
        self._scan.set_filters(*scan_filters)

        self._dest_folder = google_cloud_bucket_folder

        self._log_level = log_level
        if set_up_logger_on_init:
            self._setup_logger(log_file_name=log_file_path)
        self._post_work_action = lambda x: x
        self._copy_action = self._upload_blob

    def _create_dest_tree_folder(self, files: list, do_create_tree: bool = True):
        """
        destination - goggle cloud storage bucket, so do nothing - pass
        :param files:
        :param do_create_tree:
        :return:
        """
        pass

    def _upload_blob(self, src, dst):
        """
        this function wall be run in self.run method (default is shutils.copy2 func)
        :param src: str - path to source file
        :param dst: str - path for bucket folder desination
        :return: None
        """
        blob = self._gcs_bucket.blob(dst)
        blob.upload_from_filename(src)

    def run(self, do_copy=True):
        return super().run(do_copy=do_copy, do_create_tree=False)


class xBackupGCS(xCopyGCS):
    """
    backup selected source files to google cloud storage bucket
    create log file with name: backup type (FULL or INCREMENTAL) + name given by param log_file_path in folder, given by the same param. Date of last change this file will be use in INCREMENTAL backup work

    Class do two types of backup:
      full - select all source files that match the given filters; copy its to folder in given bucket; avter coping trying switch off arhive attribute of source files
      incremental - add RED filter to given filters list: if use_A_atrib = True and OS = Windows add filterArchAttrib, else finds the latest date of change log-file and use in last low_level for filterFileDateRange filter. So backup will be done only for source files, older then this date, or having a-atribute switchin on

    Connection to google cloud storage executed outside the class
    Example:
        smb_src = <path to source files>

        path_key = <path to json google key file>
        client = gc_storage_connect(path_key)
        bsk = dc_storage_bucket(client, '<bucket name>')
        gcs_folder = msec_add2name('INC_BACKUP')
        log_file = <path to log-file (parent dir must exists)>

        cw = xBackupGCS(source_base_dir=smb_src, log_level=logging.INFO,
                  backup_type=backup_types.INC,
                  google_bucket=bsk, log_file_path=log_file,
                  google_cloud_bucket_folder=gcs_folder,
                  scan_filters=filters)

        cw.run()

    """

    def __init__(self, source_base_dir: str = '', google_bucket: storage.Bucket = None,
                 google_cloud_bucket_folder: str = '', log_level=logging.DEBUG, scan_filters: list = list(),
                 log_file_path: str = '', backup_type: backup_types = backup_types.FULL,
                 use_A_atrib: bool = True) -> None:
        assert log_file_path != '', 'must set path to log_file'

        super().__init__(source_base_dir=source_base_dir, google_bucket=google_bucket,
                         google_cloud_bucket_folder=google_cloud_bucket_folder, log_level=log_level,
                         scan_filters=scan_filters, log_file_path=log_file_path, set_up_logger_on_init=False)

        self._work_name = backup_type.value
        self._work_type = backup_type
        lfn = '{} {}'.format(self._work_name, Path(log_file_path).name)

        self._log_file = str(Path(log_file_path).parent.joinpath(lfn))

        self._use_A_atrib = (platform.system() == 'Windows') and use_A_atrib

        if self._work_type == backup_types.FULL:
            # full backup copy all selected files and, if OS Windows and use a-atrib, switch archive file attrib off
            pass
        elif self._work_type == backup_types.INC:
            if self._use_A_atrib:
                self._scan.filters.append(filterArchAttrib(color=filter_color.RED))
            else:
                self._scan.filters.append(filterFileDateRange(color=filter_color.RED,
                                                              low_date=self.find_last_backup_date()))

        self._setup_logger(log_file_name=self._log_file)
        if self._use_A_atrib:
            self._post_work_action = set_archive_sttrib
        else:
            self._post_work_action = lambda x: x
        self._log.info('!' * 100)
        self._log.info('use Archive file attribute : {}'.format(self._use_A_atrib))
        self._log.info('!' * 100)

    def find_last_backup_date(self):
        """
        for INCREMENTAL backup: find all *BACKUP*.log' files in directory, given by log_file_path init param,
        select last date (with time), return it for use in date range filter as low level date
        :return: date of last written backup log file
        """

        print(Path(self._log_file).parent)
        # lst = list(Path(self._log_file).parent.glob('*/*BACKUP*.log'))
        lst = list(Path(self._log_file).parent.glob('*BACKUP*.log'))
        f_info = [file_info(str(f)) for f in lst]
        try:
            return max([f['change_date'] for f in f_info])
        except ValueError:
            return dt.datetime(day=1, month=1, year=1970)


def copy_gcs():
    filters = [filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb')]
    # filters = [filterFileExt(color=filter_color.WHITE, rule=r'py'),
    #            filterFileExt(color=filter_color.BLACK, rule=r'py')]
    # filters= list()

    sub_name = 'CPYTST_{}'.format(dt.datetime.now().strftime('%d_%m_%Y'))
    smb_src = '/run/user/1000/gvfs/smb-share:server=commd.local,share=personal/Golyshev'

    path_key = Path.home().joinpath('klu').joinpath('testgcds-340913-f781d2910762.json')
    client = gc_storage_connect(path_key)
    bsk = dc_storage_bucket(client, 'debug-backupu')

    # bsk = dc_storage_bucket(client, 'debug-backupu')

    cw = xCopyGCS(source_base_dir=smb_src, log_level=logging.INFO,
                  google_bucket=bsk, log_file_path=Path('../LOG/gcs_log.log'),
                  google_cloud_bucket_folder='TEST1',
                  scan_filters=filters)

    cw.run()


def backup_gcs():
    filters = [filterFileExt(color=filter_color.WHITE, rule=r'txt'),
               filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb')]
    # filters = [filterFileExt(color=filter_color.WHITE, rule=r'py'),
    #            filterFileExt(color=filter_color.BLACK, rule=r'py')]
    # filters= list()

    smb_src = '/run/user/1000/gvfs/smb-share:server=commd.local,share=personal/Golyshev'

    path_key = Path.home().joinpath('klu').joinpath('testgcds-340913-f781d2910762.json')
    client = gc_storage_connect(path_key)
    bsk = dc_storage_bucket(client, 'debug-backupu')
    gcs_folder = msec_add2name('TEST')
    log_file = Path('../LOG/{}.log'.format(msec_add2name('test')))

    cw = xBackupGCS(source_base_dir=smb_src, log_level=logging.INFO,
                    backup_type=backup_types.INC,
                    google_bucket=bsk, log_file_path=log_file,
                    google_cloud_bucket_folder=gcs_folder,
                    scan_filters=filters)

    pr = cw.run(do_copy=True)
    # for p in pr:
    #     print(p[0], ' --> ', p[1])
