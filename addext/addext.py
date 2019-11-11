#!/usr/bin/env python3

"""
addext
------
CLI utility to add file extensions to files without them based on PRONOM ID

Script has three modes:
* Default: Adds first file extension associated with PUID in PRONOM
* Dry run: Preview changes from Defualt mode without making any changes
to the files
* Manual: Manually choose extension to add to files when PRONOM gives several
options (Linux/macOS only)

Requires Siegfried and inquirer. See README for installation instructions
"""

import argparse
import inquirer
import logging
import json
import os
import subprocess
import sys


def _make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dryrun",
        help="Perform dry run: print would-be changes to terminal",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--manual",
        help="Manually choose extension when multiple options (Linux/macOS)",
        action="store_true",
    )
    parser.add_argument("target", help="Path to target file or directory")
    parser.add_argument("json", help="Path to PRONOM JSON file")

    return parser


def _configure_logging():
    """
    Configure logging to write to logfile created in
    user's current directory and to stdout
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("addext.log"),
            logging.StreamHandler(sys.stdout)
        ],
    )
    logger = logging.getLogger()
    return logger


def _puid_or_none(sf_matches):
    """
    From input list of dictionaries describing Siegfried
    matches for given file, return PUID or None
    """
    puid = None
    for match in sf_matches:
        if match["ns"] == "pronom":
            puid = match["id"]
    return puid


def _check_file_extension(filepath, extensions):
    """
    Return True if file extension (case-insensitive)
    is present in list, and False if not
    """
    # Get lower-cased file extension from path
    _, file_extension = os.path.splitext(filepath)
    file_extension_lower = file_extension[1:].lower()
    # Make lower-cased list
    extensions_lower = list()
    for item in extensions:
        extensions_lower.append(item.lower())
    # Check equivalency
    if file_extension_lower in extensions_lower:
        return True
    else:
        return False


def _rename_file(filepath, new_file, new_filepath, logger):
    """
    Rename file in place and report OSErrors
    """
    try:
        os.rename(filepath, new_filepath)
        logger.info(f"{filepath} renamed -> {new_file}")
    except OSError as e:
        logger.error(f"Unable to rename {filepath}. Details: {e}")


def _process_file(root, filepath, pronom_data, args, logger):
    """
    Identify and rename file, respecting user args
    """
    file_ = os.path.basename(filepath)

    # Attempt to determine PUID with Siegfried
    cmd = ["sf", "-json", filepath]
    try:
        sf_json = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        logger.error("Unable to call Siegfried. Is it installed and on path?")
        sys.exit(1)
    sf_data = json.loads(sf_json)
    puid = _puid_or_none(sf_data["files"][0]["matches"])

    # Skip file if unidentified
    if not puid:
        logger.info(f"Skipping {filepath} - format not identifiable")
        return

    # Save file format
    file_format = pronom_data[puid]["file_format"]

    # Skip file if already has one of extensions listed in PRONOM
    extensions = pronom_data[puid]["file_extensions"]
    extension_in_place = _check_file_extension(filepath, extensions)
    if extension_in_place:
        logger.info(
            f"Skipping {filepath} - already has correct extension for {file_format} ({puid})"
        )
        return

    # Skip file if no extensions listed for format in PRONOM
    if not extensions:
        logger.info(
            f"Skipping {filepath} - no extensions listed in PRONOM for {file_format} ({puid})"
        )
        return

    # If manual mode and > 1 extension available, prompt for user input
    if args.manual and len(extensions) > 1:
        # Print all known extensions
        extensions_str = ", ".join([x for x in extensions])
        logger.info(
            f"{filepath} identified as {file_format} ({puid}). Possible extensions: {extensions_str}"
        )
        # If --dryrun, continue to next file
        if args.dryrun:
            return
        # Otherwise, prompt user for extension and rename file in place
        else:
            # Use Inquirer to let user choose from list
            questions = [
                inquirer.List(
                    "extension",
                    message="Which extension would you like to add?",
                    choices=extensions,
                )
            ]
            # Get chosen extension
            answers = inquirer.prompt(questions)
            extension_to_add = answers["extension"]
            # Rename file
            new_file = f"{file_}.{extension_to_add}"
            new_filepath = os.path.join(root, new_file)
            _rename_file(filepath, new_file, new_filepath, logger)
            return

    # If default (auto) mode or only 1 extension, use first extension
    extension_to_add = extensions[0]
    new_file = f"{file_}.{extension_to_add}"
    new_filepath = os.path.join(root, new_file)
    # If --dryrun, print action to take to terminal and continue
    if args.dryrun:
        logger.info(
            f"{filepath} identified as {file_format} ({puid}). Rename {file_} -> {new_file}"
        )
        return
    # Otherwise, rename file in place
    _rename_file(filepath, new_file, new_filepath, logger)


def main():
    # Parse arguments
    parser = _make_parser()
    args = parser.parse_args()

    # Store fs references as abspaths
    target = os.path.abspath(args.target)
    pronom_json = os.path.abspath(args.json)

    # Configure logging
    logger = _configure_logging()

    # Load PRONOM JSON as dictionary
    with open(pronom_json, "r") as f:
        pronom_data = json.load(f)

    # Check if target is file
    if os.path.isfile(target):
        root = os.path.split(target)[0]
        _process_file(root, target, pronom_data, args, logger)
        return

    # If target is dir, walk recursively
    for root, _, files in os.walk(target):
        for file_ in files:
            filepath = os.path.join(root, file_)
            _process_file(root, filepath, pronom_data, args, logger)


if __name__ == "__main__":
    main()
