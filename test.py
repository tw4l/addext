# encoding: utf-8

from __future__ import (print_function, unicode_literals)

import datetime
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from os.path import join as j


#logging.basicConfig(filename='test.log', level=logging.DEBUG)
#stderr = logging.StreamHandler()
#stderr.setLevel(logging.WARNING)
#logging.getLogger().addHandler(stderr)

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


class SelfCleaningTestCase(unittest.TestCase):
    """TestCase subclass which cleans up self.tmpdir after each test"""

    def setUp(self):
        super(SelfCleaningTestCase, self).setUp()

        # tempdir for brunnhilde outputs
        self.tmpdir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmpdir):
            os.mkdirs(self.tmpdir)

    def tearDown(self):
        if os.path.isdir(self.tmpdir):
            shutil.rmtree(self.tmpdir)

        super(SelfCleaningTestCase, self).tearDown()


class TestAddextIntegration(SelfCleaningTestCase):
    """
    Integration tests. sf (Siegfried) must be installed on user's system for tests to work.
    """

    def test_dryrun(self):
        # file for terminal output
        checkfile = j(self.tmpdir, 'terminal-output.txt')
        # call addext, routing terminal output to file
        subprocess.call("python addext/addext.py -d ./test-data/ > %s" % (checkfile), 
            shell=True)
        # list of expected outputs
        checklist = ['animation is format Quicktime (x-fmt/384). Rename animation -> animation.mov', 
            'lorem-ipsum is format Acrobat PDF 1.3 - Portable Document Format (fmt/17). Rename lorem-ipsum -> lorem-ipsum.pdf', 
            'PF is format Lotus 1-2-3 Worksheet (x-fmt/114). Rename PF -> PF.wk1', 
            'TOPOREC is format WordPerfect for MS-DOS/Windows Document (x-fmt/44). Rename TOPOREC -> TOPOREC.doc', 
            'valid is format Microsoft Excel 97 Workbook (xls) (fmt/61). Rename valid -> valid.xls']
        # check contents of checkfile
        for statement in checklist:
            self.assertIn(statement, open(checkfile, 'r').read())

    def test_auto_renaming(self):
        # copy files to tmpdir
        for f in os.listdir('./test-data'):
            shutil.copy(j('./test-data', f), self.tmpdir)
        # call addext in default (auto) mode
        subprocess.call("python addext/addext.py %s" % (self.tmpdir), 
            shell=True)
        # lists of expected filenames and files that should not be found
        checklist = ['animation.mov', 'lorem-ipsum.pdf', 'PF.wk1', 
            'TOPOREC.doc', 'valid.xls']
        not_present = ['animation', 'lorem-ipsum', 'PF', 
            'TOPOREC', 'valid']
        # check for presence of renamed files
        for f in checklist:
            self.assertTrue(is_non_zero_file(j(self.tmpdir, f)))
        # check that files without extensions are not present
        for f in not_present:
            self.assertFalse(is_non_zero_file(j(self.tmpdir, f)))

    def test_with_DROID_csv(self):
        # copy files to tmpdir
        for f in os.listdir('./test-data'):
            shutil.copy(j('./test-data', f), self.tmpdir)
        # path to DROID csv
        droid_csv = j(self.tmpdir, 'droid.csv')
        # call addext in default (auto) mode
        subprocess.call("python addext/addext.py %s" % (self.tmpdir), 
            shell=True)
        # lists of expected filenames and files that should not be found
        checklist = ['animation.mov', 'lorem-ipsum.pdf', 'PF.wk1', 
            'TOPOREC.doc', 'valid.xls']
        not_present = ['animation', 'lorem-ipsum', 'PF', 
            'TOPOREC', 'valid']
        # check for presence of renamed files
        for f in checklist:
            self.assertTrue(is_non_zero_file(j(self.tmpdir, f)))
        # check that files without extensions are not present
        for f in not_present:
            self.assertFalse(is_non_zero_file(j(self.tmpdir, f)))


if __name__ == '__main__':
    unittest.main()