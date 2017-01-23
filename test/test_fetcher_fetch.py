import os
import tempfile
import unittest

import shutil

from file_fetched import fetch


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

    def test_hash_file(self):
        file_path = os.path.abspath('resources/sample_file.txt')
        # no hash
        entry = {}
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # MD5
        expected_digest = '9a0364b9e99bb480dd25e1f0284c8555'
        entry = {
            'md5': expected_digest
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA1
        expected_digest = '040f06fd774092478d450774f5ba30c5da78acc8'
        entry = {
            'sha1': expected_digest
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA224
        expected_digest = '37f71ccaada9d3b7570f1389bfb7dcc587f4af8ba96d5718a260f55a'
        entry = {
            'sha224': expected_digest
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA256
        expected_digest = 'ed7002b439e9ac845f22357d822bac1444730fbdb6016d3ec9432297b9ec9f73'
        entry = {
            'sha256': expected_digest
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA384
        expected_digest = '5406ebea1618e9b73a7290c5d716f0b47b4f1fbc5d8c5e78c9010a3e01c18d8594aa942e3536f7e01574245d3' +\
                          '4647523'
        entry = {
            'sha384': expected_digest
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA512
        expected_digest = 'b2d1d285b5199c85f988d03649c37e44fd3dde01e5d69c50fef90651962f48110e9340b60d49a479c4c0b53f5' +\
                          'f07d690686dd87d2481937a512e8b85ee7c617f'
        entry = {
            'sha512': expected_digest
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # unsupported algorithm
        entry = {
            "this doesn't exist": "no hash"
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))

    def test_hash_file_wrong_hash(self):
        file_path = os.path.abspath('resources/sample_file.txt')
        # MD5
        entry = {
            'md5': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA1
        entry = {
            'sha1': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA224
        entry = {
            'sha224': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA256
        entry = {
            'sha256': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA384
        entry = {
            'sha384': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))
        # SHA512
        entry = {
            'sha512': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))

    def test_hash_file_multiple_hashes(self):
        file_path = os.path.abspath('resources/sample_file.txt')
        # correct hashes
        entry = {
            'md5': '9a0364b9e99bb480dd25e1f0284c8555',
            'sha1': '040f06fd774092478d450774f5ba30c5da78acc8'
        }
        self.assertTrue(fetch._hash_file(entry=entry, file_path=file_path))
        # wrong MD5
        entry = {
            'md5': 'this is not a hash',
            'sha1': '040f06fd774092478d450774f5ba30c5da78acc8'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))
        # wrong MD5
        entry = {
            'md5': '9a0364b9e99bb480dd25e1f0284c8555',
            'sha1': 'this is not a hash'
        }
        self.assertFalse(fetch._hash_file(entry=entry, file_path=file_path))

    def test_run_with_hash(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            url = 'file:resources/sample_with_hash.json'
            fetch.run(list_url=url, save_dir=tmp_dir)
            # file should have been created and no .partial left
            expected_path = os.path.join(tmp_dir, 'test.txt')
            self.assertTrue(os.path.exists(expected_path))
            self.assertFalse(os.path.exists(expected_path + '.partial'))
        finally:
            shutil.rmtree(tmp_dir)

    def test_run_with_wrong_hash(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            url = 'file:resources/sample_with_wrong_hash.json'
            fetch.run(list_url=url, save_dir=tmp_dir)
            # file should have been downloaded as .partial,
            # but since hash doesn't match, the expected_path shouldn't exist
            expected_path = os.path.join(tmp_dir, 'test.txt')
            self.assertFalse(os.path.exists(expected_path))
            self.assertTrue(os.path.exists(expected_path + '.partial'))
        finally:
            shutil.rmtree(tmp_dir)

    def test_translate_g_drive_url(self):
        # /open?id=<id>
        url = 'https://drive.google.com/open?id=1'
        new_url = fetch._translate_g_drive_url(url=url)
        self.assertEqual('https://drive.google.com/uc?export=download&id=1', new_url)
        # /file/d/<id>
        url = 'https://drive.google.com/file/d/2'
        new_url = fetch._translate_g_drive_url(url=url)
        self.assertEqual('https://drive.google.com/uc?export=download&id=2', new_url)
        # /file/d/<id>/view
        url = 'https://drive.google.com/file/d/3/view'
        new_url = fetch._translate_g_drive_url(url=url)
        self.assertEqual('https://drive.google.com/uc?export=download&id=3', new_url)
        # /uc?export=download&id=<id>
        url = 'https://drive.google.com/uc?export=download&id=4'
        new_url = fetch._translate_g_drive_url(url=url)
        self.assertEqual(url, new_url)

    def test_g_drive_url(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            fetch.run(list_url='file:resources/sample_drive.json', save_dir=tmp_dir)
        finally:
            shutil.rmtree(tmp_dir)
