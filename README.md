# :wastebasket: Duplicate File Cleaner

Find and remove duplicate files - content hash, batch delete, dry run.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![No Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)

Duplicate File Cleaner is a lightweight, dependency-free command-line tool that finds and removes duplicate files on your system. It compares files by their content hash (SHA-256 by default) or by filename, lets you preview deletions with a dry run, and can export the results to TXT, JSON, or CSV.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Output Examples](#output-examples)
- [Keep Strategies](#keep-strategies)
- [Export Formats](#export-formats)
- [Contributing](#contributing)
- [License](#license)
- [Sponsor](#sponsor)

---

## Features

| Feature | Description |
|---|---|
| Content hash scan | Find duplicates by SHA-256/MD5/SHA1 file content comparison |
| Filename scan | Find files with the same name in different directories (`--by-name`) |
| Batch delete | Remove all duplicates at once, keeping one copy per group |
| Dry run | Preview which files would be deleted without actually deleting (`--dry-run`) |
| Keep strategies | Choose which copy to keep: first, newest, or oldest (`--keep`) |
| Export | Save the duplicate list to TXT, JSON, or CSV |
| Size filter | Ignore small files below a size threshold (`-m`) |
| Recursive | Scan subdirectories by default; opt out with `--no-recursive` |
| Zero dependencies | Pure Python standard library only |

## Installation

No installation or dependencies required. Just clone the repository and run with Python 3.8+.

```bash
git clone https://github.com/yourusername/duplicate-cleaner.git
cd duplicate-cleaner
```

Verify Python version:

```bash
python --version   # Python 3.8 or higher
```

## Usage

### Scan for duplicates (by content hash)

```bash
python main.py scan /path/to/dir
```

### Scan for duplicates by filename

```bash
python main.py scan /path/to/dir --by-name
```

### Delete duplicates with a dry-run preview

```bash
python main.py delete /path/to/dir --dry-run
```

### Delete duplicates (keeping the first copy)

```bash
python main.py delete /path/to/dir
```

### Delete duplicates, keep the newest copy

```bash
python main.py delete /path/to/dir --keep newest
```

### Export the duplicate list to a file

```bash
python main.py export /path/to/dir -o duplicates.txt
```

Export as JSON or CSV:

```bash
python main.py export /path/to/dir -o duplicates.json
python main.py export /path/to/dir -o duplicates.csv
```

### Ignore files smaller than 1 MB, use MD5

```bash
python main.py scan /path/to/dir -m 1048576 --algorithm md5
```

### Scan only the top-level directory (no subdirectories)

```bash
python main.py scan /path/to/dir --no-recursive
```

### All options

```
python main.py --help
```

```
usage: duplicate-cleaner [-h] {scan,delete,export} ...

Find and remove duplicate files by content hash or filename.
No dependencies required.

positional arguments:
  {scan,delete,export}  Available commands
    scan                Scan a directory and list duplicate files.
    delete              Delete duplicate files (keep the first).
    export              Export the duplicate file list to a file.
```

## Output Examples

Scan a directory:

```
$ python main.py scan ~/Pictures

Found 2 duplicate group(s) by content hash.
  Total files scanned:    5
  Duplicate files found:   2

Group 1 (2 files):
  KEEP   /home/user/Pictures/vacation/sunset.jpg (3.2 MB)
  DELETE /home/user/Pictures/backup/sunset_copy.jpg (3.2 MB)

Group 2 (3 files):
  KEEP   /home/user/Pictures/photo.jpg (1.5 MB)
  DELETE /home/user/Pictures/trip/photo.jpg (1.5 MB)
  DELETE /home/user/Pictures/old/photo.jpg (1.5 MB)

Potential wasted space: 6.2 MB
```

Delete with dry run:

```
$ python main.py delete ~/Documents --dry-run

Found 1 duplicate group(s) by content hash.
  Total files scanned:    2
  Duplicate files found:   1

Group 1 (2 files):
  KEEP   /home/user/Documents/report.pdf (512.0 KB)
  DELETE /home/user/Documents/copy/report.pdf (512.0 KB)

--- DRY RUN (no files will be deleted) ---
  [DRY RUN] Would delete: /home/user/Documents/copy/report.pdf (512.0 KB)

Would delete 1 file(s), freeing 512.0 KB.
```

Delete (real):

```
$ python main.py delete ~/Documents

Found 1 duplicate group(s) by content hash.
  Total files scanned:    2
  Duplicate files found:   1

Group 1 (2 files):
  KEEP   /home/user/Documents/report.pdf (512.0 KB)
  DELETE /home/user/Documents/copy/report.pdf (512.0 KB)

--- Deleting duplicates ---
  Deleted: /home/user/Documents/copy/report.pdf (512.0 KB)

Deleted 1 file(s), freeing 512.0 KB.
Done.
```

## Keep Strategies

When deleting duplicates, you can choose which copy to keep with `--keep`:

| Strategy | Description |
|---|---|
| `first` (default) | Keep the first file in alphabetical path order |
| `newest` | Keep the most recently modified file |
| `oldest` | Keep the least recently modified file |

```bash
python main.py delete ~/Pictures --keep newest
```

## Export Formats

| Format | Extension | Description |
|---|---|---|
| TXT | `.txt` | Human-readable report with KEEP/DELETE tags |
| JSON | `.json` | Structured data with group, keep, and delete fields |
| CSV | `.csv` | Tabular format with group, action, and filepath columns |

The format is inferred from the output file extension. Unrecognised extensions default to TXT.

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) for guidelines on submitting issues, feature requests, and pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Sponsor

If you find this project helpful, please consider supporting it:

[![Sponsor on Afdian](https://img.shields.io/badge/Sponsor-Afdian-orange.svg)](https://afdian.com/a/JingJingZ)
