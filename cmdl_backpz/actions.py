"""Classes for do something actions on files

    How its work:
    Setting up some action class by give it:
    source dir path;
    list of white or|and black filter for filter files by name, subpath, extension, date, date range, size range. White filters applies first, black filters applies on result of white filters work;
    destination base dir - in this dir will be placed files from source
    destination_subdir - subname for directory in destination base for root of source directory dir tree
    prefix - prefix for subname for directory in destination base for root of source directory dir tree
    delimiter - delimiter string for split prefix and subname for directory in destination base for root of source directory dir tree

    so finaly root destination dir make from prefix, delimiter and destination_subdir as: <prefix><delimiter><destination_subdir>, and full path to copied ar backuped files will be: <destination_base>/<prefix><delimiter><destination_subdir>

    new_folder_rule - class for create new root destination dir if directory with such name already exist.
    archive_format - string for valid arhive file extension (zip for zip-archive) or empty string for acton with no arhivating

    example of use (for copy work):
        # create filters for select xls(m|b|x), py (exclude pyc and ipynb) files
        filters = [filterFileExt(color=filter_color.WHITE, rule=r'xls'),
                   filterFileExt(color=filter_color.WHITE, rule=r'py'),
                   filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
                   filterFileExt(color=filter_color.BLACK, rule=r'ipynb')]

        cw = xCopyZ(source_base_dir=r'/home/egor/git/jupyter/housing_model', log_level=logging.INFO,
                    destination_base_dir='/home/egor/T', destination_subdir='model', scan_filters=filters,
                    new_folder_rule=incRule())# , archive_format='zip')

        # scan directory '/home/egor/git/jupyter/housing_model';
        # filtering selected files;
        # in base destination dir '/home/egor/T' create subdir 'model'; if this subdir alredy exist create subdir 'model_1' ('model_2' etc);
        # copy selected source file to this subdir preserving the source directories structure

        cw.run()

    Casses:

    abcActionZ - abstruct base action class.
    Methods:
        _do_scan - scan source directory tree, filter files by given filter rules
        _do_copy - copy source files to destination directories (save source dirs tree struct)
        _do_zip - copy source files to zip-archive file in destination base directory
        _setup_logger - init logging object, save log-message in log-file, display its in console
        _create_dest_tree_folder - create source directory tree inside destinationa base directory
    Properties:
         source_folder - return source directory full path
         destination_base - return destination base directory full path
    Absstuct method:
        run - do some work (define in child class

    Childs:
    class xCopyZ - do copy files work

"""
import logging
import sys
import zipfile
from shutil import copy2

from cmdl_backpz.new_folder import *
from cmdl_backpz.scan import *


def set_archive_sttrib(file_path, AAtrib_ON=True):
    """
    Switch UO or DOWN archive file attribute - work on MS Windows OS
    :param file_path:
    :param AAtrib_ON: True - Switch attribute ON, False- OFF
    :return: windows system command attr return
    """

    if AAtrib_ON:
        return subprocess.check_output(['attrib', '+a', file_path])
    else:
        return subprocess.check_output(['attrib', '-a', file_path])

class abcActionZ(ABC):

    def __init__(self, source_base_dir: str, destination_base_dir: str,
                 destination_subdir: str = '', prefix: str = '', delimiter: str = '_',
                 log_level=logging.DEBUG, scan_filters: list = list(),
                 new_folder_rule: abcNewFolderExistsRule = errorRule(),
                 archive_format:str = '') -> None:
        """
        :param source_base_dir: str or pathlike - root of source directory subtree
        :param destination_base_dir: str of pathlike - root of destination subtree
        :param destination_subdir: str - name for destination dir in destination base dir
        :param prefix: str - prefix for result name for destination dir in destination base dir (may be name of work)
        :param delimiter: str - delimiter for split prefix, subname and sufix in resulting name for destination dir in destination base dir
        :param log_level: level for loggi-message
        :param scan_filters: list - list of abcFilter-objects - for filter source files
        :param new_folder_rule: abcNewFolderExistsRule's object, for resolve existing destination dir conflict
        :param archive_format: str - empty string = no archive operation, any valid archive file extension - archive destination files
        """
        assert Path(source_base_dir).exists(), 'source dir must exists'
        assert Path(destination_base_dir).exists(), 'destination base dir must exists'

        self._source = source_base_dir
        self._dest_base = destination_base_dir

        self._scan = xScan(start_path=self.source_folder)
        self._scan.set_filters(*scan_filters)

        self._new_fold = newFolder(strBaseFolder=self.destination_base,
                                   sub_name=destination_subdir, prefix=prefix, delimiter=delimiter,
                                   exsist_rule=new_folder_rule, archive_format=archive_format)

        self._archive_format = archive_format

        self._dest_folder = self._new_fold.folder

        self._log_level = log_level
        self._setup_logger()
        self._post_work_action = lambda x: x
        super().__init__()

    @property
    def source_folder(self):
        return self._source

    @property
    def destination_base(self):
        return self._dest_base

    def _setup_logger(self):
        """
        setup logger object
        create logger object with 2 handlers: stream (with given mesage level) and file (with logger.INFO level)
        if result action work with archive file - create log file with name destination archive file and '.log' extension (instead of '.zip' extension); if destination is dir - create log-file with name of action in destination root dir
        :return: log-object
        """
        if self._archive_format:
            os.makedirs(str(self.destination_base), exist_ok=True)
            logfile = re.sub('{}$'.format(self._archive_format), 'log', str( self._dest_folder))

        else:
            # if archive = None make destination sub-dir (for this work) in destination base dir
            os.makedirs(str(self._dest_folder), exist_ok=True)
            logfile = str(self._dest_folder.joinpath('{}.log'.format(self._work_name)))

        self._log = logging.getLogger('console')
        self._log.setLevel(self._log_level)
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(self._log_level)

        fl = logging.FileHandler(logfile, mode='a')
        fl.setLevel(logging.INFO)
        self._log.addHandler(ch)
        self._log.addHandler(fl)

        if self._archive_format:
            self._log.info(
                '{dt} : {work}({arch}) work'.format(work=self._work_name, dt=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), arch=self._archive_format))
        else:
            self._log.info(
                '{dt} : {work} work'.format(work=self._work_name, dt=dt.datetime.now().strftime('%Y-%m-%d %H:%M')))
        self._log.info('SOURCE : {}'.format(str(self.source_folder)))
        self._log.info('DEST   : {}'.format(str(self._dest_folder)))
        self._log.info('')
        self._log.info('SCAN FILTERS   :')
        for f in self._scan.filters:
            self._log.info(f)
        self._log.info('=' * 100)

        return self._log

    def _create_dest_tree_folder(self, files: list, do_create_tree:bool=True):
        """
        Create destination directory subtree

        :param files: list of destinations files. Its made from source filtered files list by replace base source directiory name to destination directory base name
        :param do_create_tree: True - do create directory subtree on the disk; False - do nothing
        :return: None

        On some OS error terminate programm
        """
        dest_fld = {Path(p).parent for p in files}

        if not do_create_tree:
            return

        for dir in dest_fld:
            try:
                os.makedirs(str(dir), exist_ok=True)
            except OSError:
                self._log.error('Create folders tree OSError : {}'.format(dir))
                os._exit(-1)
        self._log.debug('create destination folders tree done')

    def _do_scan(self, only_source_operation: bool = False) -> list:
        """
        scan source directory subtree for all files;
        filter source files ;
        make paths for destination files list (replace base source dir to base destination dir);
        make working list of file pairs (src - dst);
        :param only_source_operation: bool - True - ignore destination params, return only source filtered files list
        :return: list of tuples - [(src_path, dst_paths), ]
        """
        self._scan.scan()
        self._log.info('scan source done')

        _files = self._scan.files(filtered=True)
        _cnt_files = len(_files)

        self._log.info('files in source {all_files} : after filters select {f_files} files'.format(
            all_files=self._scan.size(filtered=False), f_files=_cnt_files))

        all_weight = int(sum([f['size'] for f in self._scan.files(filtered=False)]) / 1e6)
        flt_weight = int(sum([f['size'] for f in _files]) / 1e6)

        self._log.info('size in source {all_files} (Mb) : filtered size {f_files} (Mb)'.format(
            all_files=all_weight, f_files=flt_weight))

        if only_source_operation:
            return _files
        else:
            _src_files = [f['path'] for f in _files]

            if self._archive_format:
                strSubDst = ''  # ''{0}'.format(self._new_fold._base_name)
                _dest_files = list(
                    map(lambda x: str(x['path']).replace(str(self.source_folder), strSubDst), _files))

            else:
                _dest_files = list(
                    map(lambda x: str(x['path']).replace(str(self.source_folder), str(self._dest_folder)), _files))
                # _dest_files = list(
                #     map(lambda x: str(x['path']).replace(str(self._scan.base_path), str(self._dest_folder)), _files))

            lp = list(zip(_src_files, _dest_files))
            return lp

    def _do_copy(self, src_dst, do_copy=True):
        cnt_files = len(src_dst)
        step = int(cnt_files / 100) or 1
        _logDEBMess = '{f_num} from {f_cnt}: {src} --> {dst}'
        cnt_error = 0

        for i, nf in enumerate(src_dst):
            try:
                if do_copy:
                    copy2(nf[0], nf[1])
                    self._post_work_action(nf[0])
                else:
                    with open(nf[0], 'rb') as flt:
                        # TODO: may be insert here self._post_work_action(nf[0])
                        pass
            except FileNotFoundError:
                cnt_error += 1
                self._log.error('FILE NOT FOUND - {file}'.format(file=nf[0]))

            except PermissionError:
                cnt_error += 1
                self._log.error('PERMISSION ERROR - {file}'.format(file=nf[0]))

            except:
                cnt_error += 1
                self._log.error('UNEXPECTED ERROR {err} - {file}'.format(err=sys.exc_info()[0], file=nf[0]))
                print("Unexpected error:", sys.exc_info()[0], flush=True)

            if self._log_level == logging.DEBUG:
                try:
                    self._log.debug(_logDEBMess.format(f_num=i, f_cnt=cnt_files, src=nf[0], dst=nf[1]))
                except UnicodeEncodeError:
                    self._log.error('something wrong with file name on print log')
                    try:
                        self._log.warning('something wrong with file name on print log - {}'.format(nf[1]))
                    except:
                        self._log.warning('something wrong with file name on print log')
                except:
                    self._log.error('UNEXPECTED ERROR WITH STATUS PRINT {}'.format(err=sys.exc_info()[0]))

            elif (i % step) == 0:
                print('*', end='', flush=True)
        print('')

    def _do_zip(self, src_dst):
        cnt_files = len(src_dst)
        step = int(cnt_files / 100) or 1
        _logDEBMess = '{f_num} from {f_cnt}: {src} --> {dst}'
        cnt_error = 0

        with zipfile.ZipFile(str(self._dest_folder), 'w') as myzip:
            for i, nf in enumerate(src_dst):
                try:
                    myzip.write(nf[0], arcname=nf[1])
                    self._post_work_action(nf[0])

                except FileNotFoundError:
                    cnt_error += 1
                    self._log.error('FILE NOT FOUND - {file}'.format(file=nf[0]))

                except PermissionError:
                    cnt_error += 1
                    self._log.error('PERMISSION ERROR - {file}'.format(file=nf[0]))

                if self._log_level == logging.DEBUG:
                    try:
                        self._log.debug(_logDEBMess.format(f_num=i, f_cnt=cnt_files, src=nf[0], dst=nf[1]))
                    except UnicodeEncodeError:
                        self._log.error('something wrong with file name on print log')
                        try:
                            self._log.warning('something wrong with file name on print log - {}'.format(nf[1]))
                        except:
                            self._log.warning('something wrong with file name on print log')
                    except:
                        self._log.error('UNEXPECTED ERROR WITH STATUS PRINT {}'.format(err=sys.exc_info()[0]))

                elif (i % step) == 0:
                    print('+', end='', flush=True)
        print('')

    @abstractmethod
    def run(self, do_action=True, do_create_dest_tree=True):
        pass


class xCopyZ(abcActionZ):
    """class for scanning source dir and copy filtered files into destination dir"""

    def __init__(self, source_base_dir: str, destination_base_dir: str, destination_subdir: str = '', prefix: str = '',
                 delimiter: str = '_', log_level=logging.DEBUG, scan_filters: list = list(),
                 new_folder_rule: abcNewFolderExistsRule = exsistOKRule(), archive_format: str = '') -> None:

        self._work_name = 'COPY'

        super().__init__(source_base_dir=source_base_dir, destination_base_dir=destination_base_dir,
                         destination_subdir=destination_subdir, prefix=prefix,
                         delimiter=delimiter, log_level=log_level,
                         scan_filters=scan_filters, new_folder_rule=new_folder_rule, archive_format=archive_format)

    def run(self, do_copy=True, do_create_tree=True):

        work_pair = self._do_scan()

        self._log.info('-' * 100)
        if self._archive_format:
            self._log.info('START {0} ({1}):'.format(self._work_name, self._archive_format))
        else:
            self._log.info('START {}:'.format(self._work_name))

        if len(work_pair) == 0:
            self._log.warning('nothing to {} - exit'.format(self._work_name))

        if self._archive_format:
            self._do_zip(work_pair)
        else:
            self._create_dest_tree_folder([df[1] for df in work_pair], do_create_tree=do_create_tree)
            self._do_copy(work_pair, do_copy=do_copy)

        if self._archive_format:
            self._log.info('{0} ({1}) DONE'.format(self._work_name, self._archive_format))
        else:
            self._log.info('{} DONE'.format(self._work_name))

        self._log.info(' ' * 100)

def copy():
    # filters = [filterFileExt(color=filter_color.WHITE, rule = r'xls'),]

    filters = [  # filterFileExt(color=filter_color.WHITE, rule=r'xls'),
               filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb')]
    # filters = [filterFileExt(color=filter_color.WHITE, rule=r'py'),
    #            filterFileExt(color=filter_color.BLACK, rule=r'py')]
    # filters= list()

    # sub_name = 'model_{}'.format(dt.datetime.now().strftime('%d_%m_%Y'))
    # cw = xCopyZ(source_base_dir=r'/home/egor/git/jupyter/housing_model', log_level=logging.INFO,
    #             destination_base_dir='/home/egor/T', destination_subdir=sub_name, scan_filters=filters,
    #             new_folder_rule=incRule())# , archive_format='zip')

    sub_name = 'CPYTST_{}'.format(dt.datetime.now().strftime('%d_%m_%Y'))
    cw = xCopyZ(source_base_dir=r'U:\Golyshev\Py', log_level=logging.INFO,
                destination_base_dir=r'D:\ttt', destination_subdir=sub_name, scan_filters=filters,
                new_folder_rule=incRule(), archive_format='zip')

    cw.run()

    # print('.'*100)

def main():
    pass

if __name__ == "__main__":
    copy()

    print('ALL DONE')


