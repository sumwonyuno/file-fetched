import argparse

import fetcher
from fetcher import fetch

parser = argparse.ArgumentParser()
parser.add_argument('-list_url', required=True, help='URL of files to download')
parser.add_argument('-save_dir', required=True, help='directory to save files to')

args = parser.parse_args()
fetch.run(list_url=args.list_url, save_dir=args.save_dir)
