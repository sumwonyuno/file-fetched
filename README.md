A Python package that downloads files and supports additional functionality.

#Overview
##Features
- Download a specified list of files to a specified directory
- Check downloaded files match given hash values

##Supported URL schemes
- file
- http
- https

##Supported File hash algorithms
- MD5
- SHA1
- SHA224, SHA256, SHA384, SHA512

# Requirements
Python version >= 3.4

Python packages:
- *certifi* - for HTTPS certificates

#Install
__From URL (Latest release)__

```
pip3 install https://github.com/sumwonyuno/file-fetched/releases/download/v0.1.0/file-fetched-0.1.0.tar.gz
```

__From Source__

```
git clone git@github.com:sumwonyuno/file-fetched.git
cd file-fetched
python3 setup.py sdist
cd dist
pip3 install file-fetched-0.1.0.tar.gz
```

#Usage

```
python3 -m file_fetched -list_url <URL> -save_dir <directory>
```

##Arguments
- *list_url* - URL to a JSON array of files to download
- *save_dir* - directory to download files to

##Examples
```
python3 -m file_fetched -list_url file:queue.json -save_dir output
```
```
python3 -m file_fetched -list_url https://example.com/queue.json -save_dir ~/Downloads
```

#Reference
##list_url JSON format

```json
[
  {
    "file": "(<subdirectory>/)*<filename>",
    "url": "<URL>",
    "<hash algorithm>": "<value>" 
  }
]
```
Each entry in the JSON array is a file to download.
- *file* - (required) filename to save as. subdirectories may be included.
- *url* - (required) direct download URL of the file
- *hash algorithm* - (optional) specific hash algorithm and hash value to check (e.g. MD5).
  Multiple hash algorithms and values may be specified (e.g. MD5, SHA1).

##Pseudocode
1. Check *list_url* and *save_dir* are provided
1. Download JSON file at *list_url*
1. For each entry in JSON file:
   1. If *file* exists in *save_dir*, continue to next entry
   1. Download file at *url* to *save_dir*/*file*.partial
   1. For each *hash algorithm*:
      1. check hash value against *file*.partial
   1. If any hash values does not match, leave *file*.partial alone, continue to next entry
   1. If all hash values match, rename *file*.partial to *file*
