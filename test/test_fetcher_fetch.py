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

    def test_run_local(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            fetch.run(list_url='file:resources/sample.json', save_dir=tmp_dir)
            expected_path = os.path.join(tmp_dir, 'test.txt')
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path) as f:
                self.assertEqual('content', f.read())
        finally:
            shutil.rmtree(tmp_dir)

    def test_run_https(self):
        tmp_dir = tempfile.mkdtemp()
        url = 'https://raw.githubusercontent.com/sumwonyuno/file-fetched/dev/test/resources/sample_github.json'
        try:
            fetch.run(list_url=url, save_dir=tmp_dir)
            expected_path = os.path.join(tmp_dir, 'from_github.txt')
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path) as f:
                self.assertEqual('content', f.read())
        finally:
            shutil.rmtree(tmp_dir)

    def test_run_http(self):
        tmp_dir = tempfile.mkdtemp()
        url = 'http://pastebin.com/raw/EbQj4FZF'
        # the contents should be the following text:
        # [
        #   {
        #     "name": "from_pastebin.txt",
        #     "url": "http://pastebin.com/raw/SNTseZLu"
        #   }
        # ]
        # the contents of SNTseZLu should be the following:
        expected_content = "this text is on pastebin"
        try:
            fetch.run(list_url=url, save_dir=tmp_dir)
            expected_path = os.path.join(tmp_dir, 'from_pastebin.txt')
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path) as f:
                self.assertEqual(expected_content, f.read())
        finally:
            shutil.rmtree(tmp_dir)
