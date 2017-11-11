#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crawls XML output from Ross Spencer's pronom-xml-export 
(https://github.com/exponential-decay/pronom-xml-export)
and writes selected info into a sqlite db.

Tim Walsh
November 2017

"""

import argparse
import os
from lxml import etree, objectify
import sqlite3

def _make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", 
        help="Path of PRONOM XML export directory")
    parser.add_argument("destination", 
        help="Path of directory to write sqlite db")

    return parser

def main():

    # parse arguments
    parser = _make_parser()
    args = parser.parse_args()

    # make abspaths for source and dest dirs
    source = os.path.abspath(args.source)
    dest = os.path.abspath(args.destination)

    # create sqlite db
    db = os.path.join(dest, 'pronom.db')
    conn = sqlite3.connect(db)
    conn.text_factory = str  # allows utf-8 data to be stored
    cursor = conn.cursor()

    # create db tables
    cursor.execute("DROP TABLE IF EXISTS puids")
    cursor.execute("DROP TABLE IF EXISTS extensions")
    cursor.execute("CREATE TABLE puids (id integer PRIMARY KEY AUTOINCREMENT, puid text, fileformat text, version text, default_extension text);")
    cursor.execute("CREATE TABLE extensions (id integer PRIMARY KEY AUTOINCREMENT, extension text, puid text, FOREIGN KEY (puid) REFERENCES puids(id));")

    # for PUID XML file in export, write info to dict, then db
    for rt, dirs, files in os.walk(source):
        for name in files:
            file_path = os.path.join(rt, name)

            # skip if not xml
            if not file_path.lower().endswith('xml'):
                continue

            # open xml file and strip namespaces
            tree = etree.parse(file_path)
            root = tree.getroot()
            for elem in root.getiterator():
                if not hasattr(elem.tag, 'find'): continue  # (1)
                i = elem.tag.find('}')
                if i >= 0:
                    elem.tag = elem.tag[i+1:]
            objectify.deannotate(root, cleanup_namespaces=True)

            # create dict for PUID
            puid = dict()

            # parse xml
            for target in root.findall(".//FileFormat"):
                
                # add basic info to dict
                puid['name'] = target.find("FormatName").text
                puid['version'] = target.find("FormatVersion").text.strip()
                
                # add identifiers to dict
                identifiers = list()
                for target1 in target.findall(".//FileFormatIdentifier"):
                    id_dict = dict()
                    id_dict['identifier'] = target1.find("Identifier").text
                    id_dict['id_type'] = target1.find("IdentifierType").text
                    identifiers.append(id_dict)
                puid['identifiers'] = identifiers

                # add external signatures to dict
                ext_sigs = list()
                for target2 in target.findall(".//ExternalSignature"):
                    sig_dict = dict()
                    sig_dict['sig_id'] = target2.find("ExternalSignatureID").text
                    sig_dict['signature'] = target2.find("Signature").text
                    sig_dict['sig_type'] = target2.find("SignatureType").text
                    ext_sigs.append(sig_dict)
                puid['ext_sigs'] = ext_sigs

            # parse info from puid dict
            format_name = puid['name']
            format_version = puid['version']
            
            # always only one PUID
            pronom_ids = [x['identifier'] for x in puid['identifiers'] if x['id_type'] == "PUID"]
            if pronom_ids:
                pronom_id = pronom_ids[0]
            else:
                pronom_id = ''
            
            # 0 to many extensions - keep all in list and save first value separately
            file_exts = [x['signature'] for x in puid['ext_sigs'] if x['sig_type'] == "File extension"]
            if file_exts:
                default_ext = file_exts[0]
            else:
                default_ext = ''

            # write into db puid table
            cursor.execute("INSERT INTO puids(puid, fileformat, version, default_extension) VALUES (?,?,?,?);", (pronom_id, format_name, format_version, default_ext))
            puid_pk = cursor.lastrowid # get pk of row written
            # write extensions into extensions table
            for ext in file_exts:
                cursor.execute("INSERT INTO extensions(extension, puid) VALUES (?,?);", (ext, puid_pk))

    # close db
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()