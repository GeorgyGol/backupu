# Backupz
Backup and copying files while maintaining the directory structure, with starting and setting parameters from the command 
line (for use in assigned tasks and scripts).

Both for backup and for copying, filters are available by file extension, by name, by the full path, both black lists and white lists.

Archiving (zip) of the final set is also available.

Implemented backup:
1. full
2. incremental
3. differential

For backups, the archive attribute of the file is used.

**The working version is for MS Windows only**


## Requirements
**Requires:**  Python 3.3 and above.
The info.py module (analysis of a scanned list of files - not available in scripts from the command line, available 
only in Python codes) uses pandas 22 (and above).

**Used modules:**
_argparse, logging, os, re, datetime, subprocess, zipfile, abc, shutil, sys,_

**Operating system:** MS Windows (the file attribute is "archived").

## Installation:

```
pip install git + https: //github.com/GeorgyGol/backupz.git
```

## Usage
After installation, you can use the backupz command in scripts and / or command line:

```
 > backupz --version
backupz.py 0.2.0
```

```
 > backupz -h
 

usage: backupz.py [-h] [/n NAME] /s SOURCE /d DESTINATION [/z]
                  [/w { b_full, b_inc, b_diff, copy}]
                  [/l { info, debug, error, none, warn, critical}]
                  [-e EXCLUDE_EXTENSIONS] [+e ONLY_EXTENSIONS]
                  [-f EXCLUDE_FOLDERS] [+f ONLY_FOLDERS] [-n EXCLUDE_NAMES]
                  [+n ONLY_NAMES] [--version]

Backup (full, inc or diff) and copy files from SOURCE to DESTINATION

optional arguments:
  -h, --help            show this help message and exit
  /n NAME, --name NAME  name for work (will be in log)
  /s SOURCE, --source SOURCE
                        Source dir (one) for backup or copy (can be network path)
  /d DESTINATION, --destination DESTINATION
                        Target dir (one) for backup or copy (can be network path)
  /z, --zip             ZIP-Archive destination
  /w { b_full, b_inc, b_diff, copy}, --work { b_full, b_inc, b_diff, copy}
                        backup (full, incremental or diff) or copy
  /l { info, debug, error, none, warn, critical}, --log_level { info, debug, error, none, warn, critical}
                        log with log-level or none - default=info
  -e EXCLUDE_EXTENSIONS, --exclude-extensions EXCLUDE_EXTENSIONS
                        black list: exclude files with these extensions,
                        separated by comma
  +e ONLY_EXTENSIONS, --only-extensions ONLY_EXTENSIONS
                        white list: work only with files with these
                        extensions, separated by comma
  -f EXCLUDE_FOLDERS, --exclude-folders EXCLUDE_FOLDERS
                        black list: exclude these folders, separated by comma
  +f ONLY_FOLDERS, --only-folders ONLY_FOLDERS
                        white list: work only with these folder and included
                        in
  -n EXCLUDE_NAMES, --exclude-names EXCLUDE_NAMES
                        black list: exclude files with these names, separated
                        by comma (using re.search
  +n ONLY_NAMES, --only-names ONLY_NAMES
                        white list: work only with files with these names,
                        separated by comma (using re.search
  --version             show program's version number and exit

for work parameters from file use: backupz @<filename>
```

```
 > backupz /s "c:\test" /d "d:\test" /n "Full TEST backup" -e "tmp, xml, csv, lnk" -f "@Recycle" -n "\~\$" /w "b_full"
```
 
 performs a full backup (does not take into account the archive 
 attribute, applies all the specified filters, after the backup 
 resets the archive attribute for all copied files), does not 
 backup files with tmp, xml, csv and lnk extensions, does not 
 backup everything that is in the folder @Recycle (the folder is 
 checked as part of the full path, anywhere in the path), files 
 with the name ~ $ are not backed up. A subfolder FULL_21_01_2020 
 is created in the d: \ test folder, all selected files are 
 written to it with the same folder structure (next line do the same)
 
```
 > backupz @params.txt
```

parameters are read from a file `params.txt`. 

`params.txt` - text file, may be like this:  

```buildoutcfg
/s c:\test
/d d:\test
/n Full TEST backup
-e tmp, xml, csv, lnk
-f @Recycle
-n \~\$
/w b_full
```

## How it works:
1. The source directory is scanned (```scan.py``` module, ```os.walk``` is used), a list of files with full paths is created
2. Filters are applied to the list (the virtual class for the 
filter in the same module is ```FFilter```, 
ready-made filters are the classes ```x_extension_list``` 
(by file extensions), ```x_folders``` (by the path), 
```x_names``` (by name), ```x_archive``` 
(by the "archive" attribute - for backup is applied 
automatically depending on the selected plan))
3. the target backup folder is created (the virtual class 
for creating the folder is ```X_SPATH```, the implementation 
is ```x_path_date_inc``` (in the folder specified as a target, 
a subfolder of the form ```<backup type>_<date in the format dd_mm_YYYY>_<backup number for this day>``` iscreated), 
```x_path_copy``` is used as the target the one specified in 
the parameters, no intermediate subfolders are created)
4. a folder structure is created inside the target backup 
folder that repeats the original one (empty folders - with 
filtered files - are not created)
5. Inside the target structure, the source files are copied. 
In the case of a full or incremental backup, 
the archive attribute for the source files is reset. 
When copying and differential backup, the attribute remains 
unchanged.
6. if archiving is used, a zip archive is created inside the 
target folder, the source files with paths are copied to this 
archive.
7. inside the target backup folder is placed a log file with 
the selected logging level (at debug level, the copy results 
for each file will be recorded)

_When using backupz as a script, the target folder (p. 2) is always created_


