#!/usr/bin/env python3

"""
Save selected information from PRONOM exports
to JSON file, using PUID as key

PRONOM exports available from Ross Spencer:
https://github.com/exponential-decay/
pronom-archive-and-skeleton-test-suite

Positional args:
pronom_export: Path to directory containing PRONOM XML exports
json_path: Path for new JSON file
"""

import json
from lxml import etree, objectify
import os
import sys


def main():

    # Save abspaths for args
    pronom_export = os.path.abspath(sys.argv[1])
    json_path = os.path.abspath(sys.argv[2])

    # Create dict to store data
    puids = dict()

    # Walk pronom_exports and parse XML files
    for root_dir, _, files in os.walk(pronom_export):
        for file_ in files:
            # Save filepath
            file_path = os.path.join(root_dir, file_)

            # Skip file if not XML
            if not file_path.lower().endswith('xml'):
                continue

            # Open XML file and strip namespaces
            tree = etree.parse(file_path)
            root = tree.getroot()
            for elem in root.getiterator():
                if not hasattr(elem.tag, 'find'):
                    continue
                i = elem.tag.find('}')
                if i >= 0:
                    elem.tag = elem.tag[i + 1:]
            objectify.deannotate(root, cleanup_namespaces=True)

            # Create dict to save format information
            format_info = dict()
            puid = ''
            file_extensions = list()

            # Parse XML
            for target in root.findall('.//FileFormat'):

                # Save format and version to format info dict
                format_info['file_format'] = target.find('FormatName').text
                format_info['version'] = target.find('FormatVersion').text.strip()

                # Save PUID to variable
                for target1 in target.findall('.//FileFormatIdentifier'):
                    id_type = target1.find('IdentifierType').text
                    if id_type == 'PUID':
                        puid = target1.find('Identifier').text

                # Save file extensions to list
                for target2 in target.findall('.//ExternalSignature'):
                    signature_type = target2.find('SignatureType').text
                    if signature_type == 'File extension':
                        file_extensions.append(target2.find('Signature').text)

            # Add file extensions list to format info dict
            format_info['file_extensions'] = file_extensions

            # Add to dict with PUID as key
            puids[puid] = format_info

    # Write dict to file as JSON
    with open(json_path, 'w') as f:
        json.dump(puids, f, indent=2)


if __name__ == '__main__':
    main()
