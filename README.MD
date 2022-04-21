# BackupU

## Three command line utilities and Python modules are introduced
### For what
For backing up files that have passed through fairly widely customizable filters.   
 Filters by string parameters (path, filename, extension) are based on Python regular expressions (some may not work). Utilities work from the command line - they can be used in scheduled tasks.   
The `infou` utility allows you to configure options for the `copyu` and `backupu` utilities (the utility accepts all copy and backup options, but does not perform any actions - except for displaying a list of files on the screen).    
In addition, the utility can be used, for example, to analyze the sizes of files of different types (pass the output to a csv-file with further analysis).   
The utilities work over the network (with the appropriate protocols connected), do not stop working in case of errors, write the error to the log file (and show it in the console).    
The utilities work on both OS Windows and Linux (Ubuntu 18.04).

### command line utilities
**backupu** - for backup files   
**copyu**   - for copy files   
**infou**   - for show files info in concole   

Backup, copy or display information about a file from the *SOURCE*, while maintaining the directory tree.

    Installation
    pip install git+https://github.com/GeorgyGol/backupu
    
### Usage example:

    copyu ~s="/home/egor/git/jupyter/housing_model" ~d="/home/egor/T" ~n="test work" ~e="overwrite" -e="pyc,xls?" +e="py;sqlite? txt" -f="\.git" -n="_;~" +n="year$" ~l="info" +d="2020/01/01-2021/12/31"

or   

    copyu @copyTest.params

Copy from "/home/egor/git/jupyter/housing_model" to "/home/egor/T/test work" all files with:   
   - an extension that includes a combination of "py", "sqlite\<any character\>" and "txt", 
   - exclude from copying everything that is in the folder ".git", 
   - exclude everything that has "_;~" in the name, 
   - eclude files modified outside the date range "2020/01/01-2021/12/31", 
   - exclude files with the "pyc" extension and all Excel-files from copying, 
   - copy only files whose names are end with "year$", 
   - display the operation log on the screen in "info" mode (a log file is created in the target directory, in which the title of the operation and errors are written), 
   - if there is a target folder, merge folders.

    backupu ~s="/home/egor/git/jupyter/housing_model" ~d="/home/egor/T" ~n="test work" ~w="full" -e="pyc,xls?" +e="py;sqlite? txt" -f="\.git" -n="_;~" +n="year$" ~l="info" +d="2020/01/01-2021/12/31"
    
or   

    backupu @full_backup.params
 
Perform a full backup using the same parameters (copy all files that passed the filters; if you work in MS Windows, reset the "archive" attribute for each file).  
 In the case of a backup, a subfolder is created in the target folder according to the following rule: \<backup type\>\_BACKUP\_\<date of backup\>. If there is a target folder, the name of the target folder will be incremented - the files are by no means combined.
 
    backupu ~s="/home/egor/git/jupyter/housing_model" ~d="/home/egor/T" ~n="test work" ~w="inc" -e="pyc,xls?" +e="py;sqlite? txt" -f="\.git" -n="_;~" +n="year$" ~l="info" +d="2020/01/01-2021/12/31"   

or   

    backupu @inc_backup.params


Perform an incremental backup according to the same parameters: only files with the "archive" attribute set (if working in MS Windows) or files whose modification date is greater than the date of the last log file in the "/home/egor/T" folder.   

When adding the "+z" parameter in cases of copying or backup, the target will be a zip archive file with a name built according to the rules for constructing a folder name. Log files in this case will be created in the base target folder (they are not transferred to the archive)

    infou ~s="/home/egor/git/jupyter/housing_model" ~d="/home/egor/T" ~n="test work" ~w="inc" -e="pyc,xls?" +e="py;sqlite? txt" -f="\.git" -n="_;~" +n="year$" ~l="info" +d="2020/01/01-2021/12/31"   

or   

    infou @some_params.params


Prints to the console the paths, modification dates, size, extension, mode, name and state of the "archived" attribute for each file that passed the filters, in csv file format (delimiter = ";"). Redirecting output to a file - OS means.


#### Params descrioptions:
Utilities are launched with command line parameters or with a file in which these parameters are collected; the parameters are approximately the same for all three utilities, but they are not the same.

**Valid parameters**
  
<blockquote><b>Attention!!! The tilde sign - ~ - is used as a sign denoting the parameter, except for the -a parameter (disable work with archive file attributes) - because the signs "-" and "+" are used to define "white" and "black" filters (below in parameters). For filters - "-" and "+", for other parameters - "~"</b></blockquote>

**Tilde params (common)**
<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>~n</td>
<td>--name</td>
<td>name for work (used in the log file; when copying (copyu) a subfolder is created in the target folder with name = this parameter)</td>
</tr>
<tr>
<td>~s</td>
<td>--source</td>
<td>Source path (one) – required parameter</td>
</tr>
<tr>
<td>~d</td>
<td>--destination</td>
<td>Target base path (one) for backup or copy (can be specified for infou, but not used)</td>
</tr>
<tr>
<td>~l</td>
<td>--log_level</td>
<td>Log with log-level or none (<i>debug</i> will print information about processing each file; doesn't work in infou)</td>
</tr>
<tr>
<td>+z</td>
<td>--zip</td>
<td>zip-archive destination</td>
</tr>
</table>

**backupu only params**
<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>~w</td>
<td>--work</td>
<td>backup type: full | inc <br>(full or incremental)</td>
</tr>
<tr>
<td>-a</td>
<td>--not-archive</td>
<td>(with a minus)<br>Do not use the archive attribute of the file - works only in MS Windows. When you disable the archive attribute (and in Linux), for incremental backup, the date of the last backup is used, which is determined by the date of the log file</td>
</table>

**copyu only params**
<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>~e</td>
<td>--exist_dest</td>
<td>if destination already exists do... - overwrite | new | error <br>
write over (merge), create a new subfolder in Target base path, or throw an error</td>
</tr>
</table>

**Filter options:**   
Filters are white and black. Black ones exclude files from the resulting list, white ones include "only files" them. String filters (filenames, path parts, extensions) are set according to Python's regular expression rules.
For white filters, the order of the parameters in the line or params-file matters.   

*Remember: the minus and plus signs are used for filter parameters. "-" means black filter, "+" - white*   

<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>-e</td>
<td>--exclude-extensions</td>
<td>black list: exclude files with these extensions, separated by comma (or semicolon, or space)</td>
</tr>
<tr>
<td>+e</td>
<td>--include-extensions</td>
<td>white list: include only files with these extensions, separated by comma (or semicolon, or space)</td>
</table>

<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>-f</td>
<td>--exclude-folders</td>
<td>black list: exclude these folders, separated by comma (or semicolon, or space)</td>
</tr>
<tr>
<td>+f</td>
<td>--include-folders</td>
<td>white list: include only these folders, separated by comma (or semicolon, or space)</td>
</table>

<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>-n</td>
<td>--exclude-names</td>
<td>black list: exclude files with these names, separated by comma (or semicolon, or space)</td>
</tr>
<tr>
<td>+n</td>
<td>--include-names</td>
<td>white list: include only files with these names, separated by comma (or semicolon, or space)</td>
</table>

<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>-d</td>
<td>--exclude-dates</td>
<td>black list: date (last file modification) range <YYYY/mm/dd-YYYY/mm/dd>, if high date omited - use now</td>
</tr>
<tr>
<td>+d</td>
<td>--include-dates</td>
<td>white list: date (last file modification) range <YYYY/mm/dd-YYYY/mm/dd>, if high date omited - use now</td>
</table>

<table>
<tr>
<td>short</td>
<td>full</td>
<td>description</td>
</tr>
<tr>
<td>-s</td>
<td>--exclude-size</td>
<td>black list: size (in mBt) range <0-1e3>, if high level omited - extra large</td>
</tr>
<tr>
<td>+s</td>
<td>--include-size</td>
<td>white list: size (in mBt) range <0-1e3>, if high level omited - extra large</td>
</table>

--version – show utilities version

**for work parameters from file use: \<utility name\>@\<filename\>'**   
It is allowed to put parameters in a text file and run utilities with a single parameter - the file name. The launch in this case will look like this:
   
    copyu @<params file path>   
    backupu @<params file path>   
    infou @<params file path>

**example of params file (for backupu):**   

    --source=/home/egor/git/jupyter/housing_model
    --destination=/home/egor/T
    --work=full
    --name=test work
    --exclude-extensions=pyc,xls?
    --include-extensions=py;sqlite? txt
    --exclude-folders=\.git \.idea
    --include-folders=/BLOCKS_DB/
    --exclude-names=_;~
    --include-names=year$;month
    --log_level=info
    --include-dates=2020/01/01-2021/12/31

### Python modules descriptions

Will be soon