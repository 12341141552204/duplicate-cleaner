# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-29

### Added

- Initial release of Duplicate File Cleaner.
- `scan` command: find duplicate files by content hash (SHA-256, MD5, or SHA1).
- `scan --by-name` option: find files with duplicate filenames across directories.
- `delete` command: remove duplicate files, keeping one copy per group.
- `--dry-run` flag: preview which files would be deleted without deleting.
- `--keep` strategy: choose which copy to keep (`first`, `newest`, `oldest`).
- `export` command: write the duplicate list to TXT, JSON, or CSV.
- `-m` / `--min-size` option: ignore files smaller than a threshold.
- `--no-recursive` option: scan only the top-level directory.
- `--algorithm` option: choose hash algorithm (sha256, md5, sha1).
- Two-pass scanning: group by file size first, then hash only potential duplicates.
- Human-readable file size formatting in all output.
- Wasted space calculation for each duplicate group.
- Command-line help and examples via `argparse`.
- MIT License.
- Contributing guide and issue/PR templates.
