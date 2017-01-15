import json
import os

import sys
import urllib.request
from json import JSONDecodeError
from urllib.error import URLError

import certifi


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
    print('Retriving list of files to download from URL %s' % list_url)
    try:
        with urllib.request.urlopen(list_url, cafile=certifi.where()) as f:
            json_data = json.loads(f.read().decode('UTF-8'))
    except URLError as e:
        print(e, file=sys.stderr)
        print('unable to retrieve URL %s. exiting.' % list_url, file=sys.stderr)
        sys.exit(1)
    except JSONDecodeError as e:
        print(e, file=sys.stderr)
        print('unable to parse JSON from URL %s exiting.' % list_url, file=sys.stderr)
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
            with urllib.request.urlopen(entry['url'], cafile=certifi.where()) as f:
                with open(save_path, 'wb') as output:
                    output.write(f.read())
        except URLError as e:
            print(e, file=sys.stderr)
            print('unable to retrieve file %s. exiting.' % entry['url'], file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print(e, file=sys.stderr)
            print('unable to save to path %s. skipping.' % save_path, file=sys.stderr)
        print('Finished downloading URL %s to path %s' % (entry['url'], save_path))
    print('Done')
