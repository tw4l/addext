#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Adds file extensions to files based on their PUIDs.

Tim Walsh
November 2017

"""

import argparse
import csv
import inquirer
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
try:
    # python3
    from urllib.request import urlopen
except ImportError:
    # fall back to python 2's urllib2
    from urllib2 import urlopen

def _make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dryrun", 
        help="Perform dry run: print would-be changes to terminal", 
        action="store_true")
    parser.add_argument("-m", "--manual", 
        help="Manually choose extension to add to files when PRONOM gives several options (not available in Windows)", 
        action="store_true")
    parser.add_argument("--droid_csv", 
        help="Path to DROID CSV (created by DROID or Siegfried) for files",
        action="store")
    parser.add_argument("file", 
        help="Path to file or files where extensions will be added")

    return parser

def download_pronom_db():
    """
    Download pronom.db from Github to script directory.
    """
    
    print("Addext could not find pronom.db file in script directory.")
    print("Downloading file now. This should only be necessary once.")

    # url for pronom.db
    url = "https://github.com/timothyryanwalsh/addext/blob/master/addext/pronom.db?raw=true"

    # download file to current directory
    file_name = "pronom.db"
    u = urlopen(url)
    f = open(file_name, 'wb')
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        f.write(buffer)
    f.close()
    print("File successfully downloaded.")

def main():

    # parse arguments
    parser = _make_parser()
    args = parser.parse_args()

    source = os.path.abspath(args.file)

    # connect to pronom.db
    THIS_DIR = os.path.dirname(os.path.realpath(__file__))
    db = os.path.join(THIS_DIR, 'pronom.db')
    # download copy of pronom.db if not in same directory as script
    if not os.path.isfile(db):
        download_pronom_db()
    try:
        conn = sqlite3.connect(db)
        conn.text_factory = str  # allows utf-8 data to be stored
        cursor = conn.cursor()
    except:
        print("Error connecting to pronom.db database. Shutting down.")
        sys.exit(69)

    # create DROID CSV if user didn't pass one to script
    if args.droid_csv:
        droid_csv = os.path.abspath(args.droid_csv)
    else:
        # create tempdir for droid csv
        tmpdir = tempfile.mkdtemp()
        tmpdir_path = os.path.abspath(tmpdir)
        droid_csv = os.path.join(tmpdir_path, 'droid.csv')
        # create droid csv with siegfried
        subprocess.call("sf -droid '%s' > '%s'" % (source, droid_csv), shell=True)

    # loop through files
    for rt, dirs, files in os.walk(source):
        for f in files:
            filepath = os.path.join(rt, f)

            # search DROID CSV for path, get PUID
            with open(droid_csv) as droid:
                r = csv.reader(droid)
                for row in r:
                    if row[3] == filepath:
                        puid = row[14]
                        fileformat = row[16]
            
            # if PUID found, carry on
            if puid:
                # if manual, give option to user whenever > 1 possible extension is found
                if args.manual:
                    # get list of possible extensions using puid
                    sql = "SELECT id from puids WHERE puid='%s';" % (puid)
                    cursor.execute(sql)
                    pk = cursor.fetchone()[0]
                    sql = "SELECT extension from extensions WHERE puid='%s';" % (pk)
                    cursor.execute(sql)
                    file_ext_list = [item[0] for item in cursor.fetchall()]
                    # if >= 1 extension found, carry on
                    if file_ext_list:
                        # check if dry run - if so, print results to terminal
                        if args.dryrun == True:
                            print("File %s is format %s (%s). Possible extensions: %s" % (filepath, fileformat, puid, ', '.join(map(str, file_ext_list))))
                        else:
                            # if only one possible extension, just add it and report to user
                            if len(file_ext_list) == 1:
                                # append filename to file in-place
                                file_ext = file_ext_list[0]
                                new_filepath = filepath + "." + file_ext
                                new_filename = f + "." + file_ext
                                # check if file already ends in correct extension before adding
                                if not filepath.lower().endswith(file_ext):
                                    try:
                                        os.rename(filepath, new_filepath)
                                        print("File " + filepath + " only has one possible extension. Renamed to " + new_filename)
                                    except OSError as err:
                                        print("Error renaming file " + filepath + ": ", err)
                                else:
                                    print("File " + filepath + " already has correct extension. Skipping file.")
                            # if > 1 extension, give control to user
                            else:
                                # get user input
                                if (sys.version_info > (3, 0)):
                                    choice = input("File %s is format %s (%s). Possible extensions: %s. Add an extension? (yes/no)" % (filepath, fileformat, puid, ', '.join(map(str, file_ext_list))))
                                else:
                                    choice = raw_input("File %s is format %s (%s). Possible extensions: %s. Add an extension? (yes/no)" % (filepath, fileformat, puid, ', '.join(map(str, file_ext_list))))
                                # if input is yes, display options and apply change
                                if choice.lower() in ['yes', 'y']:
                                    # use Inquirer to let user choose from list
                                    questions = [
                                      inquirer.List('extension',
                                                    message="Which extension would you like to add?",
                                                    choices=file_ext_list,
                                                ),
                                    ]
                                    # get chosen extension
                                    answers = inquirer.prompt(questions)
                                    file_ext = answers['extension']
                                    # append filename to file in-place
                                    new_filepath = filepath + "." + file_ext
                                    new_filename = f + "." + file_ext
                                    try:
                                        os.rename(filepath, new_filepath)
                                        print("File " + filepath + " renamed to " + new_filename)
                                    except OSError as err:
                                        print("Error renaming file " + filepath + ": ", err)
                                else:
                                    print("File " + filepath + " skipped.")

                    else:
                        print("File " + filepath + " identified as " + puid + ". No extensions are registered in PRONOM for this PUID. Skipping file.")
                # else, use default extension (first listed in PRONOM for PUID)
                else:
                    sql = "SELECT default_extension from puids WHERE puid='%s';" % (puid)
                    cursor.execute(sql)
                    file_ext = cursor.fetchone()[0]
                    if file_ext:
                        new_filepath = filepath + "." + file_ext # filename + extension
                        new_filename = f + "." + file_ext # new filename without path
                        # check if dry run - if so, print results to stdout
                        if args.dryrun == True:
                            if not filepath.lower().endswith(file_ext):
                                print("File %s is format %s (%s). Rename %s -> %s" % (filepath, fileformat, puid, f, new_filename))
                            else:
                                print("File " + filepath + " already has correct extension. Skipping file.")
                        else:
                            # check if file already ends in correct extension before adding
                            if not filepath.lower().endswith(file_ext):
                                try:
                                    os.rename(filepath, new_filepath)
                                    print("File " + filepath + " renamed to " + new_filename)
                                except OSError as err:
                                    print("Error renaming file " + filepath + ": ", err)
                            else:
                                print("File " + filepath + " already has correct extension. Skipping file.")
                    else:
                        print("File " + filepath + " identified as " + puid + ". No extensions are registered in PRONOM for this PUID. Skipping file.")
            else:
                print("File " + filepath + " not identified. Skipping file.")

    # delete DROID tempdir if applicable
    if not args.droid_csv:
        shutil.rmtree(tmpdir_path)

    # close db, print finished message
    conn.commit()
    conn.close()
    print("Process complete.")

if __name__ == '__main__':
    main()