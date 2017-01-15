import os
import tempfile
import unittest

import shutil

from fetcher import fetch


class TestFetcherFetch(unittest.TestCase):
    def test_run_args(self):
        try:
            fetch.run(list_url='', save_dir='')
            # should not go here
            self.assertTrue(False)
        except SystemExit:
            # should go here
            pass

    def test_run(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            fetch.run(list_url='file:resources/sample.json', save_dir=tmp_dir)
            expected_path = os.path.join(tmp_dir, 'test.txt')
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path) as f:
                self.assertEqual('content', f.read())
        finally:
            shutil.rmtree(tmp_dir)
