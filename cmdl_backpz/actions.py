"""using FileList from scan for actions on files from scanned (and filtered) list
XBackup_A - backup files filtered by archive-attribute;
    make full backup (ignored archive attrib for making source-file list, but reset it for backuped files)
         incremental backup (filtered files with raised archive attr, back its up and reset archve attr )
    also can make full copy (completele ignore archive attribute)
    can zip copy ar backup work

    optionally for each backup or commission a separate subfolder is created in the target folder,
    the subfolder is created according to the rule defined by the descendant of the X_SPATH class

    in this module there are two make-subfolder-rules-class:
    x_path_date_inc - make subfolder from type of work (copy, inc or full backup) and current date
    x_path_copy - not making subfolders at all, working in target folder

    each work can be logged, log-file placed in save-dir (using rulls-class), log-levels given by params,
    records of each single file had writen have DEBUG level, errors have ERROR-level

    ================================================================================
    will be class for deleting given files (filterd or not) in source location
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


class xCopyZ:
    """class for scanning source folder and copy filtered files into destination folder with source folder struct"""

    def __init__(self, source_folder: str, destination_forled: str,
                 new_folder: str = '', prefix: str = '', delimiter: str = '_',
                 log_level=logging.DEBUG, scan_filters: list = list(),
                 new_folder_rule: abcNewFolderExistsRule = exsistOKRule()) -> None:

        self.source_folder = source_folder
        self.destination_base = destination_forled

        self._scan = xScan(start_path=self.source_folder)
        self._scan.set_filters(*scan_filters)

        self._new_fold = newFolder(strBaseFolder=self.destination_base,
                                   sub_name=new_folder, prefix=prefix, delimiter=delimiter,
                                   exsist_rule=new_folder_rule)
        self._dest_folder = self._new_fold.folder

        self._log_level = log_level
        self._work_name = 'COPY'

        self._setup_logger()

    def _setup_logger(self):
        print(self._dest_folder)
        os.makedirs(self._dest_folder, exist_ok=True)

        if self.new_folder.prefix:
            logfile = self._dest_folder.joinpath('{}.log'.format(self.new_folder.prefix))
        else:
            logfile = self._dest_folder.joinpath('{}.log'.format(self._work_name))

        self._log = logging.getLogger('console')
        self._log.setLevel(self._log_level)
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(self._log_level)

        fl = logging.FileHandler(logfile, mode='a')
        fl.setLevel(logging.INFO)
        self._log.addHandler(ch)
        self._log.addHandler(fl)

        self._log.info(
            '{dt} : {work} work'.format(work=self._work_name, dt=dt.datetime.now().strftime('%Y-%m-%d %H:%M')))
        self._log.info('SOURCE : {}'.format(str(self.source_folder)))
        self._log.info('DEST   : {}'.format(str(self._dest_folder)))
        self._log.info('SCAN FILTERS   :')
        for f in self._scan.filters:
            self._log.info(f)
        self._log.info('=' * 100)

        return self._log

    @property
    def source_folder(self):
        return self._source

    @source_folder.setter
    def source_folder(self, value):
        # TODO: dangerous - must be hidden
        assert Path(value).exists(), 'source folder must exists'
        self._source = value

    @property
    def destination_base(self):
        return self._dest_base

    @destination_base.setter
    def destination_base(self, value):
        # TODO: dangerous - must be hidden
        assert Path(value).exists(), 'destination folder must exists'
        self._dest_base = value

    @property
    def scanner(self):
        # TODO: dangerous - must be hidden
        return self._scan

    @property
    def new_folder(self):
        # TODO: dangerous - must be hidden
        return self._new_fold

    def _create_dest_tree_folder(self, files: list, do_create_tree=True):
        dest_fld = {Path(p).parent for p in files}

        if not do_create_tree:
            return

        for dir in dest_fld:
            try:
                os.makedirs(dir, exist_ok=True)
            except OSError:
                self._log.error('Create folders tree OSError : {}'.format(dir))
                os._exit(-1)
        self._log.debug('create destination folders tree done')

    def _do_scan(self):
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

        _src_files = [f['path'] for f in _files]

        _dest_files = list(
            map(lambda x: str(x['path']).replace(str(self._scan.base_path), str(self._dest_folder)), _files))

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
                else:
                    with open(nf[0], 'rb') as flt:
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

    def run(self, do_copy=True, do_create_tree=True):

        work_pair = self._do_scan()

        self._log.info('-' * 100)
        self._log.info('START {}:'.format(self._work_name))

        if len(work_pair) == 0:
            self._log.warning('nothing to {} - exit'.format(self._work_name))

        self._create_dest_tree_folder([df[1] for df in work_pair])

        self._do_copy(work_pair, do_copy=do_copy)

        self._log.info('{} DONE'.format(self._work_name))
        self._log.info(' ' * 100)



class X_SPATH(ABC):
    _base_path=''
    def __init__(self, strBasePath):
        self._base_path=strBasePath

    @abstractmethod
    def subpath(self, *args, **kwargs):
        pass

class x_path_date_inc(X_SPATH):
    _str_pre=''
    _str_suff=''
    _str_dele='_'

    def __init__(self, strBasePath, prefix='', delimiter='_', month_format='%m'):
        self._base_path=strBasePath
        self._str_pre=prefix
        self._str_suff=dt.datetime.now().strftime(self._str_dele.join(['%d', month_format, '%Y']))
        self._str_dele = delimiter

    def _check_exists(self, strPath):
        if os.path.exists(strPath):
            lst_dirs = os.listdir(self._base_path)
            re_last=re.compile('{dele}{dele}(\d+)$'.format(dele=self._str_dele))
            try:
                num=sorted([int(re_last.search(p).group(1)) for p in filter(re_last.search, lst_dirs)])[-1]+1
            except IndexError:
                num=0
            return strPath + self._str_dele*2 + str(num)
        else:
            return strPath

    def subpath(self, *args, **kwargs):
        try:
            self._str_pre=kwargs['prefix']
        except:
            pass
        strPrePath=os.path.join(self._base_path, '{pre}{dele}{suff}'.format(pre=self._str_pre,
                                                                       suff=self._str_suff,
                                                                       dele=self._str_dele))
        return self._check_exists(strPrePath)
    def __str__(self):
        strRet='subpath creator: on curent day with inc on exists'
        return strRet

class x_path_copy(X_SPATH):
    def subpath(self, *args, **kwargs):
        return self._base_path
    def __str__(self):
        ret='return source path for copy task'
        return ret


class x_work_types:

    _dct=dict()

    def __init__(self, c_copy='COPY', c_bu_full='FULL', c_bu_inc='INC', c_bu_diff='DIFF'):
        self._dct=dict(zip([self.copy, self.backup_full, self.backup_inc, self.backup_diff],
                           [c_copy, c_bu_full, c_bu_inc, c_bu_diff]))

    @property
    def copy(self):
        return 'copy'

    @property
    def backup_full(self):
        return 'b_full'

    @property
    def backup_inc(self):
        return 'b_inc'

    @property
    def backup_diff(self):
        return 'b_diff'

    def __contains__(self, key):
        return key in {self.copy, self.backup_diff, self.backup_inc, self.backup_full}

    def __getitem__(self, ind):
        return self._dct[ind]

    def __str__(self):
        return 'prefixes for: copy - {copy}, backup-full - {b_full}, backup-inc - {b_inc}, backup-diff - {b_diff}' \
                .format(copy=self._dct[self.copy], b_full=self._dct[self.backup_full], b_inc=self._dct[self.backup_inc],
                        b_diff=self._dct[self.backup_diff])

WORK_TYPE=x_work_types()


class XBackup_A:
    _files=None
    _strSavePath=''
    _name=''
    _sub_path_rule=None
    _pre_subpath=list()
    _err_list=[]
    _logger=None
    _work_type=None

    def __init__(self, strWorkPath='', strSavePath='',
                 SaveSubFolderRule=None, name='', work_type=WORK_TYPE, *filters):
        assert isinstance(WORK_TYPE, x_work_types), 'Init XBackup_A: wrong work types'
        assert isinstance(SaveSubFolderRule, type(None)) | issubclass(type(SaveSubFolderRule), X_SPATH), 'Init XBackup_A: wrong work SaveSubFolderRule'
        #issubclass(type(f), FFilter)

        if strSavePath.startswith(os.path.abspath(strWorkPath)):
            raise FileExistsError('Can\'t backup to working folder: {0} -> {1}'.format(strWorkPath, strSavePath))
        self._strSavePath= os.path.normpath(strSavePath)
        self._files= scan.FileList(strWorkPath)

        if SaveSubFolderRule:
            self._sub_path_rule = SaveSubFolderRule
        else:
            self._sub_path_rule = x_path_date_inc(self._strSavePath)

        self._name=name
        self._work_type=work_type

    def filters(self, *filters):
        f_arch = scan.x_archive('archive')
        self._files.filters(f_arch, *filters)

    @property
    def path_rule(self):
        return self._sub_path_rule

    @path_rule.setter
    def path_rule(self, class_path_rules):
        if isinstance(class_path_rules, X_SPATH):
            self._sub_path_rule=class_path_rules
        else:
            raise TypeError

    @property
    def name(self):
        return self._name
    @property
    def work_path(self):
        return self._files.work_path
    @property
    def save_path(self):
        return self._strSavePath

    @property
    def error_list(self):
        return self._err_list

    def __str__(self):
        strRet='''
BACKUP {name}
SOURCE PATH - {s_path} 
SAVE PATH - {path}
DEST PATH RULE - {pathrule}
{path_refixes} 
{files_info}
========================================'''.format(name=self._name, path=self._strSavePath, s_path=self._files.work_path,
                                                   files_info=str(self._files), path_refixes=str(self._work_type),
                                                   pathrule=str(self._sub_path_rule))
        return strRet

    def scan(self, full=False):
        self._files.scan()
        if full:
            try:
                self._files.switch_filter(filter_name='archive', switch_value=False)
            except KeyError:
                pass
            return self._files.filtered_files
        else:
            try:
                self._files.switch_filter(filter_name='archive', switch_value=True)
            except KeyError:
                pass
            return self._files.filtered_files

    def _switch_archive(self, strPath, str_comm='-A'):
        subprocess.check_output(['attrib', str_comm, strPath])

    def backup(self, work_type=WORK_TYPE.backup_inc, zip=False, log_level=None):
        assert work_type in WORK_TYPE, 'BACKUP func: Wrong work type; {}'.format(work_type)

        strWorkDir = self._sub_path_rule.subpath(prefix=self._work_type[work_type])
        print(self.__str__())
        print('work type - ', self._work_type[work_type])

        if log_level:
            self._setup_logger('BACKUP', strWorkDir, log_level)
            self._log(logging.INFO, self.__str__())
            self._log(logging.INFO, 'work type: {}'.format(self._work_type[work_type]))
        else:
            self._logger=None

        if zip:
            print('ZIP-BACKUP WORK ({}), START SCANING...'.format(work_type), end='', flush=True)
        else:
            print('BACKUP WORK ({}), START SCANING...'.format(work_type), end='', flush=True)

        lst_files=self.scan(full=work_type==self._work_type.backup_full)

        if zip:
            return self._zip_files(strWorkDir, lst_files, strWork=work_type)
        else:
            return self._copy_files(strWorkDir, lst_files, strWork=work_type)

    def _log(self, level, message):
        if self._logger:
            self._logger.log(level, message)

    def _zip_files(self, strWorkDir, list_files, strWork=WORK_TYPE.copy):
        assert strWork in WORK_TYPE, 'ZIP files: wrong work type'

        if len(list_files)==0:
            print('NOTHING ZIP, done')
            self._log(logging.INFO, 'NOTHING {}-ZIP, done.'.format(strWork.upper()))
            return []
        print('RUN ZIP FOR {} FILES...'.format(len(list_files)), flush=True)
        self._log(logging.INFO, 'RUN {1}-ZIP FOR {0} FILES...'.format(len(list_files), strWork.upper()))

        os.makedirs(strWorkDir, exist_ok=True)
        zp_file = os.path.join(strWorkDir, '{file}.zip'.format(file=os.path.split(strWorkDir)[-1]))

        cnt_done=0
        cnt_error=0

        with zipfile.ZipFile(zp_file, 'w') as myzip:
            for i, file in enumerate(list_files):
                #str_filename=file #.encode("cp1251").decode('cp1251').encode('utf8').decode('utf8')
                print('\t{2} from {3}:\tzip-{4} {0} to {1}...'.format(file, zp_file, i, len(list_files), strWork),
                      end='', flush=True)

                myzip.write(file) #, arcname=str_filename)

                if strWork in [WORK_TYPE.backup_full, WORK_TYPE.backup_inc]:
                    self._switch_archive(file)
                print('done', flush=True)
                self._log(logging.DEBUG, '{0} from {1}: {2} - done'.format(i + 1, len(list_files), file))
                cnt_done += 1
            print('DONE')
            self._log(logging.INFO,
                      'done for {0} files: ok for {1} and {2} errors'.format(len(list_files), cnt_done, cnt_error))
        return list_files

    def _copy_files(self, strWorkDir, list_files, strWork=WORK_TYPE.copy):
        assert strWork in WORK_TYPE, 'Copy files: wrong work type'
        if len(list_files)==0:
            print('NOTHING {}, done.'.format(strWork.upper()))
            self._log(logging.INFO, 'NOTHING {}, done.'.format(strWork.upper()))
            return []
        self._err_list=[]

        print('RUN FOR {} FILES...'.format(len(list_files)), flush=True)
        self._log(logging.INFO, 'RUN {1} FOR {0} FILES...'.format(len(list_files), strWork.upper()))

        if strWorkDir[-1]!=os.path.sep:
            strWorkDir+=os.path.sep
        work_list = [(f, os.path.abspath(f.replace(self._files.work_path, strWorkDir))) for f in list_files]

        new_folders = set([os.path.dirname(pr[1]) for pr in work_list])
        for dir in new_folders:
            os.makedirs(dir, exist_ok=True)

        cnt_done=0
        cnt_error=0

        for i, pair in enumerate(work_list):
            try:
                print('\t{2} from:\t{3} {4} {0} to {1}...'.format(pair[0], pair[1], i+1,
                                                                  len(work_list), strWork.lower()), end='', flush=True)
            except UnicodeEncodeError:
                print('something wrong with file name on print log', end='')
                try:
                    self._log(logging.WARNING, 'something wrong with file name on print log - {}'.format(pair[1]))
                    print(' - ', pair[1])
                except:
                    print('')
                    self._log(logging.WARNING, 'something wrong with file name on print log')
            except:
                self._log(logging.ERROR, 'UNEXPECTED ERROR WITH STATUS PRINT {}'.format(err=sys.exc_info()[0]))
                print("Unexpected error:", sys.exc_info()[0], flush=True)

            try:
                copy2(pair[0], pair[1]) # maybe using xcopy windows command
                if strWork in [WORK_TYPE.backup_full, WORK_TYPE.backup_inc]:
                    self._switch_archive(pair[0])
            except FileNotFoundError:
                cnt_error+=1
                self._log(logging.ERROR, 'FILE NOT FOUND - {file}'.format(file=pair[0]))
                print('ERROR', flush=True)
            except PermissionError:
                cnt_error += 1
                self._log(logging.ERROR, 'PERMISSION ERROR - {file}'.format(file=pair[0]))
                print('ERROR', flush=True)
            except:
                cnt_error += 1
                self._log(logging.ERROR, 'UNEXPECTED ERROR {err} - {file}'.format(err=sys.exc_info()[0], file=pair[0]))
                print("Unexpected error:", sys.exc_info()[0], flush=True)
            else:
                print('done', flush=True)
                self._log(logging.DEBUG, '{0} from {1}: {2} - done'.format(i+1, len(work_list), pair[0]))
                cnt_done+=1


        self._log(logging.INFO, 'done for {0} files: ok for {1} and {2} errors'.format(len(work_list), cnt_done, cnt_error))
        print('DONE')

        return work_list

    def switch_filter(self, filter_name='', switch_value=True):
        self._files.switch_filter(filter_name=filter_name, switch_value=switch_value)

    def _setup_logger(self, strWorkName, strDestPath, level):
        _logger = logging.getLogger(strWorkName)

        strFileName = '{file}_{date}.log'.format(file=strWorkName, date=dt.datetime.now().strftime('%d_%m_%Y'))

        # print(os.path.join(strDestPath, strFileName))
        try:
            fh = logging.FileHandler(os.path.join(strDestPath, strFileName), mode='w', encoding='cp1251')
        except FileNotFoundError:
            os.makedirs(strDestPath)
            fh = logging.FileHandler(os.path.join(strDestPath, strFileName), mode='w', encoding='cp1251')

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        #_logger.setLevel(logging.INFO)
        _logger.setLevel(level)
        # add handler to logger object
        _logger.addHandler(fh)
        self._logger=_logger
        return _logger


class XCopy_A(XBackup_A):
    def backup(self, work_type=WORK_TYPE.backup_inc, zip=False, log_level=None):
        raise NotImplementedError('Not backup from copy class')
    def _switch_archive(self, strPath, str_comm='-A'):
        raise NotImplementedError('Not backup from copy class')

    def __init__(self, strWorkPath='', strSavePath='',
                 SaveSubFolderRule=None, name='', work_type=WORK_TYPE, *filters):
        assert isinstance(WORK_TYPE, x_work_types), 'Init XCopy_A: wrong work types'
        assert isinstance(SaveSubFolderRule, type(None)) | issubclass(type(SaveSubFolderRule), X_SPATH), 'Init XCopy_A: wrong work SaveSubFolderRule'
        #issubclass(type(f), FFilter)

        if strSavePath.startswith(os.path.abspath(strWorkPath)):
            raise FileExistsError('Can\'t copy to working folder: {0} -> {1}'.format(strWorkPath, strSavePath))
        self._strSavePath= os.path.normpath(strSavePath)
        self._files= scan.FileList(strWorkPath)

        if SaveSubFolderRule:
            self._sub_path_rule = SaveSubFolderRule
        else:
            self._sub_path_rule = x_path_copy(self._strSavePath)

        self._name=name
        self._work_type=work_type

    def copy(self, zip=False, log_level=None):
        strWorkDir = self._sub_path_rule.subpath(prefix=self._work_type[WORK_TYPE.copy])
        if zip:
            print('ZIP WORK, START SCANING...', end='')
        else:
            print('COPY WORK, START SCANING...', end='')

        lst_files = self.scan(full=True)

        if log_level:
            self._setup_logger('COPY', strWorkDir, log_level)
            self._log(logging.INFO, self.__str__())
        else:
            self._logger = None

        if zip:
            return self._zip_files(strWorkDir, lst_files, strWork=WORK_TYPE.copy)
        else:
            return self._copy_files(strWorkDir, lst_files, strWork=WORK_TYPE.copy)

    def __str__(self):
        strRet = '''
COPY {name}
SOURCE PATH - {s_path} 
SAVE PATH - {path}
DEST PATH RULE - {pathrule}
{path_refixes} 
{files_info}
========================================'''.format(name=self._name, path=self._strSavePath,
                                                           s_path=self._files.work_path,
                                                           files_info=str(self._files),
                                                           path_refixes=str(self._work_type),
                                                           pathrule=str(self._sub_path_rule))
        return strRet


def copy():
    # filters = [filterFileExt(color=filter_color.WHITE, rule = r'xls'),]

    filters = [filterFileExt(color=filter_color.WHITE, rule=r'sqlite\d?'),
               filterFileExt(color=filter_color.WHITE, rule=r'py'),
               filterFileExt(color=filter_color.BLACK, rule=r'pyc'),
               filterFileExt(color=filter_color.BLACK, rule=r'ipynb')]
    # filters = [filterFileExt(color=filter_color.WHITE, rule=r'py'),
    #            filterFileExt(color=filter_color.BLACK, rule=r'py')]
    # filters= list()

    cw = xCopyZ(source_folder=r'/home/egor/git/jupyter/housing_model', log_level=logging.INFO,
                destination_forled='/home/egor/T', new_folder='model', scan_filters=filters,
                new_folder_rule=dateRuleInc())

    cw.run()

    # print('.'*100)

def main():
    pass

if __name__ == "__main__":

    #main()

    # f=x_path_copy('ddd')
    # print(issubclass(type(f), X_SPATH))
    # print(issubclass(type(WORK_TYPE), x_work_types))
    # print(type(None))
    # print(WORK_TYPE.copy)
    # print('copy1' in WORK_TYPE)
    # print(WORK_TYPE[WORK_TYPE.backup_inc])
    # print(WORK_TYPE)
    # print(isinstance(WORK_TYPE, x_work_types))
    copy()

    print('ALL DONE')


