# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Changed
- unsupported URL schemes will not be processed
- list_url and the URLs in list_url contents are retrieved in the same way

## [0.2.0] - 2017-01-23
### Added
- direct download support for various Google Drive URLs (e.g. /open, /file/d)

### Fixed
- support downloading large files. previously read entire file to memory first. changed to read and save file chunks.

## [0.1.0] - 2017-01-18
### Added
- download files from URL (file://, http://, https://)
- check downloaded file hash against expected hashes (e.g. MD5, SHA1)
