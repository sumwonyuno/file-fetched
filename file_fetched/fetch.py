import hashlib
import json
import os

import sys
import urllib.request
from html.parser import HTMLParser
from urllib.error import URLError

import certifi


def _hash_match(alg, file_path: str, expected_hash: str):
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            alg.update(chunk)
    # compare digest with expected hash
    return alg.hexdigest() == expected_hash


def _hash_file(entry: dict, file_path: str) -> bool:
    wrong_hash_msg = 'Expected %s hash for file %s does not match: %s'
    # this will accommodate multiple hashing algorithms
    # return False if any doesn't match
    if 'md5' in entry:
        if not _hash_match(alg=hashlib.md5(), file_path=file_path, expected_hash=entry['md5']):
            print(wrong_hash_msg % ('md5', file_path, entry['md5']), file=sys.stderr)
            return False
    if 'sha1' in entry:
        if not _hash_match(alg=hashlib.sha1(), file_path=file_path, expected_hash=entry['sha1']):
            print(wrong_hash_msg % ('sha1', file_path, entry['sha1']), file=sys.stderr)
            return False
    if 'sha224' in entry:
        if not _hash_match(alg=hashlib.sha224(), file_path=file_path, expected_hash=entry['sha224']):
            print(wrong_hash_msg % ('sha224', file_path, entry['sha224']), file=sys.stderr)
            return False
    if 'sha256' in entry:
        if not _hash_match(alg=hashlib.sha256(), file_path=file_path, expected_hash=entry['sha256']):
            print(wrong_hash_msg % ('sha256', file_path, entry['sha256']), file=sys.stderr)
            return False
    if 'sha384' in entry:
        if not _hash_match(alg=hashlib.sha384(), file_path=file_path, expected_hash=entry['sha384']):
            print(wrong_hash_msg % ('sha384', file_path, entry['sha384']), file=sys.stderr)
            return False
    if 'sha512' in entry:
        if not _hash_match(alg=hashlib.sha512(), file_path=file_path, expected_hash=entry['sha512']):
            print(wrong_hash_msg % ('sha512', file_path, entry['sha512']), file=sys.stderr)
            return False
    # if got here, either all of the hashes matched, or no hash was provided
    # assume it's OK
    return True


def _handle_url(url: str, output_file: str):
    chunk_size = 4096
    # need to handle drive.google.com differently
    if url.startswith('https://drive.google.com/'):
        _handle_g_drive_url(url=url, output_file=output_file, chunk_size=chunk_size)
    else:
        _handle_default_url(url=url, output_file=output_file, chunk_size=chunk_size)


def _handle_default_url(url: str, output_file: str, chunk_size: int):
    with urllib.request.urlopen(url, cafile=certifi.where()) as f:
        with open(output_file, 'wb') as output:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                output.write(chunk)


class GDriveParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.direct_path = None

    def handle_starttag(self, tag, attrs):
        # need to get <a id="uc-download-link" href=<direct_path>...>
        matched = False
        for attr in attrs:
            if attr[0] == 'id' and attr[1] == 'uc-download-link':
                matched = True
        if matched:
            for attr in attrs:
                if attr[0] == 'href':
                    self.direct_path = attr[1]


def _translate_g_drive_url(url: str) -> str:
    # need to have in URL https://drive.google.com/uc?export=download&id=<id>
    url_open = 'https://drive.google.com/open?id='
    url_uc = 'https://drive.google.com/uc?export=download&id='
    url_file_d = 'https://drive.google.com/file/d/'
    # translate /open to /uc for direct file download
    if url.startswith(url_open):
        url = url.replace(url_open, url_uc)
        print('Translated URL to %s' % url)
    # translate /file/d/ to /uc for direct file download
    if url.startswith(url_file_d):
        url = url.replace(url_file_d, url_uc)
        # may need to remove /view at the end of the URL
        suffix_view = '/view'
        if url.endswith(suffix_view):
            url = url.replace(suffix_view, '')
        print('Translated URL to %s' % url)
    return url


def _handle_g_drive_url(url: str, output_file: str, chunk_size: int):
    url = _translate_g_drive_url(url)
    with urllib.request.urlopen(url=url, cafile=certifi.where()) as f:
        # expecting redirects
        # if URL domain is not drive.google.com, just download URL contents
        if not f.geturl().startswith('https://drive.google.com'):
            # probably redirected to googleusercontent.com
            _handle_default_url(url=url, output_file=output_file, chunk_size=chunk_size)
            return
        # if URL domain is still drive.google.com, then not actually downloading file
        # may need to handle large files (< 25MB), will "Download anyway" page
        # need to get real download link
        print('Retrieving direct file download link; selecting \'Download anyway\' option')
        # page should only be a few KB
        parser = GDriveParser()
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            parser.feed(str(chunk))
        if not parser.direct_path:
            # workflow probably changed
            print('Unable to retrieve updated direct file download link %s. skipping.' % url,
                  file=sys.stderr)
            return
        new_url = 'https://drive.google.com' + parser.direct_path
        # need to copy cookies
        cookies = ''
        for header, value in f.info().items():
            if header == 'Set-Cookie':
                cookies += value
        headers = {'Cookie': cookies}
        request = urllib.request.Request(url=new_url, headers=headers)
        # fetch direct download URL contents
        with urllib.request.urlopen(request) as f2:
            with open(output_file, 'wb') as output:
                while True:
                    chunk = f2.read(chunk_size)
                    if not chunk:
                        break
                    output.write(chunk)


def run(list_url: str, save_dir: str):
    save_dir = os.path.abspath(save_dir)
    # make sure save_dir exists
    try:
        os.makedirs(save_dir, exist_ok=True)
    except OSError as e:
        print(e, file=sys.stderr)
        print('unable to use %s. exiting.' % save_dir, file=sys.stderr)
        sys.exit(1)
    print('Saving files to directory %s' % save_dir)
    # get list of files to download
    print('Retrieving list of files to download from URL %s' % list_url)
    try:
        with urllib.request.urlopen(list_url, cafile=certifi.where()) as f:
            json_data = json.loads(f.read().decode('UTF-8'))
    except URLError as e:
        print(e, file=sys.stderr)
        print('unable to retrieve URL %s. exiting.' % list_url, file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(e, file=sys.stderr)
        print('unable to process URL %s. exiting.' % list_url, file=sys.stderr)
        sys.exit(1)
    if not isinstance(json_data, list):
        print('content of URL %s is not a JSON array. exiting.' % list_url, file=sys.stderr)
        sys.exit(1)
    if not json_data:
        # empty JSON array, no need to process
        print('JSON array is empty. no files to download')
        sys.exit(0)
    print('Downloading files:')
    for entry in json_data:
        if not isinstance(entry, dict):
            print('entry is not a dict. skipping.', file=sys.stderr)
            continue
        # url and name are required
        if 'url' not in entry:
            print('missing "url" in entry. skipping.', file=sys.stderr)
            continue
        if 'name' not in entry:
            print('missing "name" in entry. skipping.', file=sys.stderr)
            continue
        print('name %s, URL %s' % (entry['name'], entry['url']))
        # make sure save path is in save_dir
        save_path = os.path.abspath(os.path.join(save_dir, entry['name']))
        if not save_path.startswith(save_dir):
            print('path %s for file %s is not in save_dir %s. not allowed. skipping.' %
                  (save_path, entry['name'], save_dir))
        # make sure parent directories exist
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        except OSError as e:
            print(e, file=sys.stderr)
            print('unable to save to path %s. skipping.' % save_path, file=sys.stderr)
            continue
        # skip if file exists
        if os.path.isfile(save_path):
            print('path %s exists. not downloading URL %s, name %s. skipping.' %
                  (save_path, entry['url'], entry['name']))
            continue
        # get file
        try:
            # save tile to .partial file first before saving as the expected file
            partial_file = save_path + '.partial'
            _handle_url(url=entry['url'], output_file=partial_file)
            # check .partial file matches any hashes
            if _hash_file(entry, partial_file):
                print('Downloaded file, all hashes match.')
                os.rename(partial_file, save_path)
            else:
                print('Downloaded file, but a hash does not match. leaving file as %s. skipping.' % partial_file,
                      file=sys.stderr)
                continue
        except URLError as e:
            print(e, file=sys.stderr)
            print('unable to retrieve file %s. exiting.' % entry['url'], file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print(e, file=sys.stderr)
            print('unable to save to path %s. skipping.' % save_path, file=sys.stderr)
        print('Finished downloading URL %s to path %s' % (entry['url'], save_path))
    print('Done')
