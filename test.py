#!/usr/bin/env python3

import os
import shutil
import subprocess
import tempfile
import unittest

from os.path import join as j

from addext.addext import _puid_or_none, _check_file_extension


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


class SelfCleaningTestCase(unittest.TestCase):
    """
    TestCase subclass which cleans up self.tmpdir after each test
    """

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


class TestIntegration(SelfCleaningTestCase):
    """
    Integration tests. sf (Siegfried) must be installed on user's system.
    """

    def test_dryrun_file(self):
        """
        Test results of dryrun on file by checking
        expected message against stdout
        """
        cmd = [
            'python3',
            'addext/addext.py',
            '-d',
            './test-data/animation',
            'addext/pronom_v95.json'
        ]
        stdout = subprocess.check_output(cmd).decode('utf-8')
        statement = 'animation identified as Quicktime (x-fmt/384). Rename animation -> animation.mov'
        self.assertIn(statement, stdout)

    def test_dryrun_dir(self):
        """
        Test results of dryrun on directory by checking
        expected messages against stdout
        """
        cmd = [
            'python3',
            'addext/addext.py',
            '-d',
            './test-data/',
            'addext/pronom_v95.json'
        ]
        stdout = subprocess.check_output(cmd).decode('utf-8')
        # Check file for presence of expected messages
        checklist = [
            'animation identified as Quicktime (x-fmt/384). Rename animation -> animation.mov',
            'lorem-ipsum identified as Acrobat PDF 1.3 - Portable Document Format (fmt/17). Rename lorem-ipsum -> lorem-ipsum.pdf',
            'PF identified as Lotus 1-2-3 Worksheet (x-fmt/114). Rename PF -> PF.wk1',
            'TOPOREC identified as WordPerfect for MS-DOS/Windows Document (x-fmt/44). Rename TOPOREC -> TOPOREC.doc',
            'valid identified as Microsoft Excel 97 Workbook (xls) (fmt/61). Rename valid -> valid.xls'
        ]
        for statement in checklist:
            self.assertIn(statement, stdout)

    def test_auto_renaming_file(self):
        """
        Test results of default auto-renaming mode for file
        """
        # Copy test file to temporary directory
        shutil.copy('./test-data/animation', self.tmpdir)
        filepath = j(self.tmpdir, 'animation')
        # Call addext in default (auto) mode
        cmd = f'python3 addext/addext.py {filepath} addext/pronom_v95.json'
        subprocess.call(cmd, shell=True)
        # Check for presence of renamed file
        renamed_filepath = j(self.tmpdir, 'animation.mov')
        self.assertTrue(is_non_zero_file(renamed_filepath))
        # Check for non-presence of original file
        self.assertFalse(is_non_zero_file(filepath))

    def test_auto_renaming_dir(self):
        """
        Test results of default auto-renaming mode for directory
        """
        # Copy test data to temporary directory
        for f in os.listdir('./test-data'):
            shutil.copy(j('./test-data', f), self.tmpdir)
        # Call addext in default (auto) mode
        cmd = f'python3 addext/addext.py {self.tmpdir} addext/pronom_v95.json'
        subprocess.call(cmd, shell=True)
        # Check for presence of renamed files
        present = [
            'animation.mov',
            'lorem-ipsum.pdf',
            'PF.wk1',
            'TOPOREC.doc',
            'valid.xls'
        ]
        for f in present:
            self.assertTrue(is_non_zero_file(j(self.tmpdir, f)))
        # Check for non-presence of original files
        not_present = [
            'animation',
            'lorem-ipsum',
            'PF',
            'TOPOREC',
            'valid'
        ]
        for f in not_present:
            self.assertFalse(is_non_zero_file(j(self.tmpdir, f)))


class TestUnit(unittest.TestCase):
    """
    Unit tests
    """

    def test_puid_or_none(self):
        """
        Unit tests for function _test_puid_or_none()
        """
        # Test input with PUID
        list_with_puid = [
            {
                "ns": "pronom",
                "id": "x-fmt/384",
                "format": "Quicktime",
                "version": "",
                "mime": "video/quicktime",
                "basis": "byte match at 4, 8 (signature 4/8)",
                "warning": "extension mismatch"
            }
        ]
        puid = _puid_or_none(list_with_puid)
        self.assertTrue(puid == 'x-fmt/384')
        # Test input with no PUID
        list_without_puid = [
            {
                "ns": "something else",
                "id": "abc123"
            }
        ]
        puid = _puid_or_none(list_without_puid)
        self.assertTrue(puid is None)

    def test_check_file_extension(self):
        """
        Unit tests for function _check_file_extension()
        """
        filepath = '/my/madeup/filepath.odt'
        # Test positive case
        pos_extensions = ['odt', 'ods', 'docx']
        self.assertTrue(_check_file_extension(filepath, pos_extensions))
        # Test case sensitivity
        caps_extensions = ['ODT']
        self.assertTrue(_check_file_extension(filepath, caps_extensions))
        # Test negative case
        neg_extensions = ['ods', 'docx', 'rtf']
        self.assertFalse(_check_file_extension(filepath, neg_extensions))


if __name__ == '__main__':
    unittest.main()
