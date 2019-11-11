## addext

### Version: 2.0.1

[![Build Status](https://travis-ci.org/timothyryanwalsh/addext.svg?branch=master)](https://travis-ci.org/timothyryanwalsh/addext)

Python script to add file extensions to files without them, based on Siegfried identification of PUID.

### Calling addext

`addext.py` takes two positional arguments:
* `target`: Path to target file or directory
* `json`: Path to addext PRONOM JSON file (`pronom_v95.json` is included in this repository for convenience. See **PRONOM JSON file** section below for instructions on how to create a new JSON file in expected format from PRONOM XML exports)

Options include:  
* `-d, --dryrun`: Perform dry run (print would-be changes to terminal instead of renaming files)
* `-m, --manual`: Manually choose extension to add to files when PRONOM gives several options (not available in Windows)

### Behavior

#### Default mode

In its default mode, `addext` adds file extensions to files if they meet a few conditions:  
* Siegfried can positively identify a PUID for the file
* There is at least one file extension associated with the PUID in PRONOM
* The file does not already have one of the extensions listed in PRONOM for that PUID (case-insensitive)

If all conditions are met, `addext` adds the file extension to the file in-place. It is recommended that you try a dry run first to evaluate the proposed changes before renaming files.

#### Manual mode

In `-m, --manual` mode, `addext` follows the following logic:
* If Siegfried cannot positively identify a PUID for the file, skip the file
* If there is only one file extension associated with the PUID in PRONOM and the file does not already have this extension (case-insensitive), add the extension
* If there is more than one file extension associated with the PUID in PRONOM and the file does not already have this extension, allow the user to choose which extension to add and then modify the filename in-place

Note that for directories with many files, going through the files one-by-one in manual mode may take some time. Running `addext` as a dry run in manual mode may help give an idea of the extent of manual choices you will be asked to make.

Due to its dependency on [Inquirer](https://github.com/magmax/python-inquirer), manual mode is not available on Windows.

### Requirements 

* Python 3.6+
* [Siegfried](https://github.com/richardlehane/siegfried)
* [Inquirer](https://github.com/magmax/python-inquirer): For selection between extension options in `-m, --manual` mode (Linux/macOS only); installed with `pip install inquirer`

### Installation

#### Install Siegfried

Install Siegfried following the instructions found [here](https://github.com/richardlehane/siegfried).

#### Install via git clone/download

The easiest way to use `addext` is to clone or download this repository and then run the script with `python3 /path/to/addext.py [options]`.

If taking this route, install additional Python library dependencies: `pip install -r requirements.txt` or `pip install inquirer` (this may require sudo permissions).

#### Install via PyPI

`addext` can also be installed via `pip install addext`. This will install a script in the `/usr/local/bin` directory (assuming a Linux/macOS installation) so that `addext` can be called from anywhere with simply `addext.py [options]`.

Note that following installation, you will need to download or create a PRONOM JSON file to use with `addext`.

### PRONOM JSON file

#### Description

The PRONOM JSON file is a lightweight representation of information from PRONOM needed for addext to function. The file contains an object for each format described with a PRONOM ID (PUID), structured like the following example:

```
"fmt/858": {
    "file_format": "Navisworks Document",
    "version": "2010",
    "file_extensions": [
      "nwd",
      "nwc"
    ]
  }
```

#### Updating the PRONOM JSON file

`pronom_v95.json` is currently up-to-date with PRONOM release v95.

To create a new PRONOM JSON file (for instance, after a new PRONOM release):  
* Get PRONOM XML export from Ross Spencer's [Release repository for The Skeleton Test Suite](https://github.com/exponential-decay/pronom-archive-and-skeleton-test-suite), which provides a set of DOIs for archives of PRONOM releases.
* Run `addext/pronom_xml_to_json.py` to create a new PRONOM JSON file from the XML exports: `python3 pronom_xml_to_json.py /path/to/pronom/export/directory pronom.json`

### Creators

* Canadian Centre for Architecture
* Tim Walsh

This project was initially developed in 2016-2017 for the [Canadian Centre for Architecture](https://www.cca.qc.ca) by Tim Walsh, Digital Archivist, as part of the development of the Archaeology of the Digital project.
