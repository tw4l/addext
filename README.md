## addext

Python script to add file extensions to files without them, based on DROID/Siegfried identification of PUID.

### Calling addext

`addext.py` takes one positional argument: the file or directory containing files for which the user wants to add file extensions.

Options include:  
* `-d, --dryrun`: Perform dry run: print would-be changes to terminal instead of renaming files.
* `-m, --manual`: Manually choose extension to add to files when PRONOM gives several options (not available in Windows).  
* `--droid_csv DROID_CSV`: Path to a DROID CSV to use for mapping files against their PUIDs. This is optional - if the user does not pass a DROID-style CSV file to addext, the program will use Siegfried to create one in a temporary directory and delete it when no longer needed.

Note: `addext.py` must be run from same directory as `pronom.db`, a SQLite database containing selected information from PRONOM for each PUID (format name, version, and associated file extensions).

### Behavior

#### Default mode

In its default mode, `addext.py` adds file extensions to files within the chosen directory if they meet a few conditions:  
* The DROID file passed by the user or created by addext positively identifies the file with a PUID.  
* There is at least one file extension associated with the PUID in PRONOM.
* The file does not already have the file extension that would be added based on the PUID record (this is case-insensitive - addext will not add ".doc" if the file already has the extension ".DOC").  

If all conditions are met, `addext.py` adds the file extension to the file in-place. It is recommended that you try a dry run first before modifying files in-place to evaluate the proposed changes.

#### Manual mode

In `-m, --manual` mode, `addext.py` follows the following logic:
* If the DROID file passed by the user or created by addext does not positively identify the file with a PUID, skip the file.  
* If there is only one file extension associated with the PUID in PRONOM and the file does not already have this extension (case-insensitive), add the extension.  
* If there is more than one file extension associated with the PUID in PRONOM and the file does not already have this extension:  
	* Check with the user if they want to add an extension (yes/no)  
	* If yes, allow the user to choose which extension to add and then modify the filename in-place.  

Note that for directories with many files, going through the files one-by-one in manual mode may take some time. Running `addext.py` as a dry run in manual mode may help give an idea of the extent of manual choices you will be asked to make.

Due to its dependency on [Inquirer](https://github.com/magmax/python-inquirer), manual mode is not available on Windows.

### Updating the PRONOM file extension database

`pronom.db` is currently up-to-date with PRONOM release: v92

To create a new database (for instance, after a new PRONOM release):  
* Use Ross Spencer's [pronom-xml-export](https://github.com/timothyryanwalsh/pronom-xml-export) to download XML files for all fmt and x-fmt PUIDs.
* Run `pronom-xml-to-sqlite.py` to create a new pronom.db database from the XML exports.

### Dependencies  

* [Siegfried](https://github.com/richardlehane/siegfried): For creating DROID-style CSVs. It is not necessary to have Siegfried installed on your system if you pass a DROID CSV file to addext with the `--droid_csv` flag.
* [Inquirer](https://github.com/magmax/python-inquirer): For selection between extension options in `-m, --manual` mode (Linux/macOS only)

### To do  
* Update script for database so it's not necessary to re-create from scratch for each release  
* Fix PyPI packaging (may need to remove automatic script generation - this is currently breaking the link to the `pronom.db` database unless a user with elevated permissions manually patches)
