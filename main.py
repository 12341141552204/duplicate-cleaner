#!/usr/bin/env python3
"""
Duplicate File Cleaner - Find and remove duplicate files using content
hashing or filename comparison. No external dependencies required.

Usage:
    python main.py scan /path/to/dir
    python main.py scan /path/to/dir --by-name
    python main.py delete /path/to/dir --dry-run
    python main.py export /path/to/dir -o duplicates.txt
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Supported hash algorithms.
HASH_ALGORITHMS = ("sha256", "md5", "sha1")

# Chunk size for reading files (1 MiB).
CHUNK_SIZE = 1024 * 1024


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def format_size(size_bytes: int) -> str:
    """Return a human-readable file size string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        A formatted string like ``"1.5 MB"``.
    """
    if size_bytes < 0:
        return "0 B"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    units = ("KB", "MB", "GB", "TB")
    size = float(size_bytes)
    for unit in units:
        size /= 1024.0
        if size < 1024.0:
            return f"{size:.1f} {unit}"
    return f"{size:.1f} PB"


def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    """Compute the hash of a file.

    Reads the file in chunks to handle large files efficiently.

    Args:
        filepath: Path to the file.
        algorithm: Hash algorithm name (``"sha256"``, ``"md5"``, ``"sha1"``).

    Returns:
        The hexadecimal digest string.

    Raises:
        ValueError: If the algorithm is not supported.
        OSError: If the file cannot be read.
    """
    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(
            f"Unsupported hash algorithm '{algorithm}'. "
            f"Choose from: {', '.join(HASH_ALGORITHMS)}."
        )

    hasher = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def find_files(
    directory: str,
    min_size: int = 0,
    recursive: bool = True,
) -> List[Path]:
    """Collect all regular files in a directory.

    Args:
        directory: Root directory to scan.
        min_size: Ignore files smaller than this many bytes.
        recursive: Whether to descend into subdirectories.

    Returns:
        A sorted list of ``Path`` objects for matching files.
    """
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    results: List[Path] = []
    if recursive:
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in filenames:
                filepath = Path(dirpath) / name
                try:
                    if filepath.is_file() and not filepath.is_symlink():
                        if filepath.stat().st_size >= min_size:
                            results.append(filepath)
                except OSError:
                    # Skip files we cannot stat (permission issues, etc.).
                    pass
    else:
        for entry in root.iterdir():
            if entry.is_file() and not entry.is_symlink():
                try:
                    if entry.stat().st_size >= min_size:
                        results.append(entry)
                except OSError:
                    pass

    results.sort()
    return results


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def scan_by_content(
    directory: str,
    min_size: int = 0,
    recursive: bool = True,
    algorithm: str = "sha256",
) -> List[List[str]]:
    """Find duplicate files by comparing content hashes.

    Uses a two-pass strategy: first group files by size, then hash only
    files that share their size with at least one other file. This avoids
    hashing every file when most are unique.

    Args:
        directory: Root directory to scan.
        min_size: Ignore files smaller than this many bytes.
        recursive: Whether to descend into subdirectories.
        algorithm: Hash algorithm to use.

    Returns:
        A list of duplicate groups. Each group is a list of file paths
        that share identical content. Only groups with two or more files
        are returned. The first file in each group is the one to keep.
    """
    files = find_files(directory, min_size, recursive)

    # Pass 1: group files by size.
    size_groups: Dict[int, List[Path]] = {}
    for filepath in files:
        try:
            size = filepath.stat().st_size
        except OSError:
            continue
        size_groups.setdefault(size, []).append(filepath)

    # Pass 2: hash only files in size groups with more than one member.
    hash_groups: Dict[str, List[str]] = {}
    for size, group in size_groups.items():
        if len(group) < 2:
            continue
        for filepath in group:
            try:
                digest = hash_file(str(filepath), algorithm)
            except OSError:
                continue
            hash_groups.setdefault(digest, []).append(str(filepath))

    # Build the list of duplicate groups (only groups with 2+ files).
    duplicates: List[List[str]] = []
    for digest, paths in hash_groups.items():
        if len(paths) >= 2:
            duplicates.append(paths)

    # Sort for deterministic output.
    duplicates.sort(key=lambda g: g[0])
    return duplicates


def scan_by_name(
    directory: str,
    min_size: int = 0,
    recursive: bool = True,
) -> List[List[str]]:
    """Find files with duplicate names.

    Two files are considered duplicates if they have the same filename
    (e.g., ``photo.jpg`` in two different subdirectories).

    Args:
        directory: Root directory to scan.
        min_size: Ignore files smaller than this many bytes.
        recursive: Whether to descend into subdirectories.

    Returns:
        A list of duplicate groups. Each group is a list of file paths
        that share the same filename.
    """
    files = find_files(directory, min_size, recursive)

    name_groups: Dict[str, List[str]] = {}
    for filepath in files:
        name = filepath.name
        name_groups.setdefault(name, []).append(str(filepath))

    duplicates: List[List[str]] = []
    for name, paths in name_groups.items():
        if len(paths) >= 2:
            duplicates.append(paths)

    duplicates.sort(key=lambda g: g[0])
    return duplicates


# ---------------------------------------------------------------------------
# Reordering (keep strategy)
# ---------------------------------------------------------------------------

def reorder_by_keep_strategy(
    duplicates: List[List[str]],
    keep: str = "first",
) -> List[List[str]]:
    """Reorder each duplicate group so the file to keep is first.

    Args:
        duplicates: List of duplicate groups.
        keep: Strategy to choose which file to keep.
            ``"first"``  - keep the first file (alphabetical order).
            ``"newest"`` - keep the most recently modified file.
            ``"oldest"`` - keep the least recently modified file.

    Returns:
        The reordered list of duplicate groups.

    Raises:
        ValueError: If ``keep`` is not a recognised strategy.
    """
    if keep not in ("first", "newest", "oldest"):
        raise ValueError(
            f"Unknown keep strategy '{keep}'. "
            "Choose from: first, newest, oldest."
        )

    if keep == "first":
        # Already sorted alphabetically; no change needed.
        return duplicates

    reordered: List[List[str]] = []
    for group in duplicates:
        # Sort by modification time.
        def mtime(path: str) -> float:
            try:
                return os.path.getmtime(path)
            except OSError:
                return 0.0

        if keep == "newest":
            sorted_group = sorted(group, key=mtime, reverse=True)
        else:  # oldest
            sorted_group = sorted(group, key=mtime)
        reordered.append(sorted_group)

    return reordered


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_duplicates(
    duplicates: List[List[str]],
    dry_run: bool = False,
) -> Tuple[int, int]:
    """Delete duplicate files, keeping the first file in each group.

    Args:
        duplicates: List of duplicate groups (first file is kept).
        dry_run: If True, print what would be deleted without deleting.

    Returns:
        A tuple of (files_deleted, bytes_freed).
    """
    deleted_count = 0
    freed_bytes = 0

    for group in duplicates:
        keep_path = group[0]
        to_delete = group[1:]
        for filepath in to_delete:
            try:
                size = os.path.getsize(filepath)
            except OSError:
                size = 0

            if dry_run:
                print(f"  [DRY RUN] Would delete: {filepath} "
                      f"({format_size(size)})")
            else:
                try:
                    os.remove(filepath)
                    print(f"  Deleted: {filepath} ({format_size(size)})")
                except OSError as exc:
                    print(f"  Error deleting {filepath}: {exc}",
                          file=sys.stderr)
                    continue

            deleted_count += 1
            freed_bytes += size

    return deleted_count, freed_bytes


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_duplicates(
    duplicates: List[List[str]],
    output_file: str,
    fmt: str = "txt",
) -> None:
    """Write the duplicate file list to a file.

    Args:
        duplicates: List of duplicate groups.
        output_file: Destination file path.
        fmt: Output format - ``"txt"``, ``"json"``, or ``"csv"``.

    Raises:
        ValueError: If the format is not recognised.
    """
    if fmt not in ("txt", "json", "csv"):
        raise ValueError(
            f"Unknown export format '{fmt}'. "
            "Choose from: txt, json, csv."
        )

    if fmt == "txt":
        with open(output_file, "w", encoding="utf-8") as f:
            for i, group in enumerate(duplicates, 1):
                f.write(f"Group {i} ({len(group)} files):\n")
                for j, path in enumerate(group):
                    tag = "KEEP" if j == 0 else "DELETE"
                    f.write(f"  [{tag}] {path}\n")
                f.write("\n")
            total_files = sum(len(g) for g in duplicates)
            f.write(f"Summary: {len(duplicates)} group(s), "
                    f"{total_files} files, "
                    f"{total_files - len(duplicates)} duplicate(s).\n")

    elif fmt == "json":
        data = {
            "total_groups": len(duplicates),
            "total_files": sum(len(g) for g in duplicates),
            "duplicates": [
                {
                    "group": i,
                    "keep": group[0],
                    "delete": group[1:],
                    "file_count": len(group),
                }
                for i, group in enumerate(duplicates, 1)
            ],
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    elif fmt == "csv":
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["group", "action", "filepath"])
            for i, group in enumerate(duplicates, 1):
                for j, path in enumerate(group):
                    action = "keep" if j == 0 else "delete"
                    writer.writerow([i, action, path])

    print(f"Exported {len(duplicates)} duplicate group(s) to {output_file}")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_duplicates(
    duplicates: List[List[str]],
    mode: str = "content",
) -> None:
    """Print a human-readable duplicate report to stdout.

    Args:
        duplicates: List of duplicate groups.
        mode: Detection mode for labeling - ``"content"`` or ``"name"``.
    """
    if not duplicates:
        print("No duplicates found.")
        return

    total_duplicates = sum(len(g) - 1 for g in duplicates)
    total_files = sum(len(g) for g in duplicates)
    label = "content hash" if mode == "content" else "file name"

    print(f"\nFound {len(duplicates)} duplicate group(s) "
          f"by {label}.")
    print(f"  Total files scanned:    {total_files}")
    print(f"  Duplicate files found:   {total_duplicates}")
    print()

    wasted_bytes = 0
    for i, group in enumerate(duplicates, 1):
        keep_path = group[0]
        print(f"Group {i} ({len(group)} files):")
        try:
            size = os.path.getsize(keep_path)
        except OSError:
            size = 0
        for j, path in enumerate(group):
            tag = "KEEP   " if j == 0 else "DELETE "
            print(f"  {tag}{path} ({format_size(size)})")
        wasted_bytes += size * (len(group) - 1)
        print()

    print(f"Potential wasted space: {format_size(wasted_bytes)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def add_scan_options(parser: argparse.ArgumentParser) -> None:
    """Add shared scan options to a subparser."""
    parser.add_argument(
        "directory",
        type=str,
        help="Directory to scan for duplicates.",
    )
    parser.add_argument(
        "--by-name",
        action="store_true",
        help="Find duplicates by filename instead of content hash.",
    )
    parser.add_argument(
        "-m", "--min-size",
        type=int,
        default=0,
        help="Minimum file size in bytes to consider (default: 0).",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not scan subdirectories (top-level only).",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="sha256",
        choices=HASH_ALGORITHMS,
        help="Hash algorithm for content scan (default: sha256).",
    )


def get_duplicates(args: argparse.Namespace) -> Tuple[List[List[str]], str]:
    """Run a scan based on the parsed arguments.

    Returns:
        A tuple of (duplicates, mode) where mode is "content" or "name".
    """
    recursive = not args.no_recursive

    if args.by_name:
        dups = scan_by_name(
            directory=args.directory,
            min_size=args.min_size,
            recursive=recursive,
        )
        return dups, "name"

    dups = scan_by_content(
        directory=args.directory,
        min_size=args.min_size,
        recursive=recursive,
        algorithm=args.algorithm,
    )
    return dups, "content"


def cmd_scan(args: argparse.Namespace) -> None:
    """Handle the ``scan`` subcommand."""
    duplicates, mode = get_duplicates(args)
    print_duplicates(duplicates, mode=mode)


def cmd_delete(args: argparse.Namespace) -> None:
    """Handle the ``delete`` subcommand."""
    duplicates, mode = get_duplicates(args)
    duplicates = reorder_by_keep_strategy(duplicates, keep=args.keep)

    print_duplicates(duplicates, mode=mode)

    if not duplicates:
        return

    if args.dry_run:
        print("\n--- DRY RUN (no files will be deleted) ---")
    else:
        print("\n--- Deleting duplicates ---")

    deleted, freed = delete_duplicates(duplicates, dry_run=args.dry_run)

    print(f"\n{'Would delete' if args.dry_run else 'Deleted'} "
          f"{deleted} file(s), freeing {format_size(freed)}.")
    if not args.dry_run:
        print("Done.")


def cmd_export(args: argparse.Namespace) -> None:
    """Handle the ``export`` subcommand."""
    duplicates, mode = get_duplicates(args)
    duplicates = reorder_by_keep_strategy(duplicates, keep=args.keep)

    print_duplicates(duplicates, mode=mode)

    if not duplicates and not args.output:
        print("No duplicates found; nothing to export.")
        return

    output = args.output or "duplicates.txt"
    fmt = output.rsplit(".", 1)[-1].lower() if "." in output else "txt"

    # Normalise non-standard extensions to txt.
    if fmt not in ("txt", "json", "csv"):
        fmt = "txt"

    export_duplicates(duplicates, output, fmt=fmt)


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="duplicate-cleaner",
        description=(
            "Find and remove duplicate files by content hash or filename. "
            "No dependencies required."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py scan ~/Pictures\n"
            "  python main.py scan ~/Downloads --by-name\n"
            "  python main.py delete ~/Documents --dry-run\n"
            "  python main.py export ~/Music -o dups.json\n"
            "  python main.py scan . -m 1048576 --algorithm md5\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan subcommand
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a directory and list duplicate files.",
        description="Scan a directory for duplicate files and display a report.",
    )
    add_scan_options(scan_parser)
    scan_parser.set_defaults(func=cmd_scan)

    # delete subcommand
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete duplicate files (keep the first).",
        description="Delete duplicate files, keeping one copy per group.",
    )
    add_scan_options(delete_parser)
    delete_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview which files would be deleted without actually deleting.",
    )
    delete_parser.add_argument(
        "--keep",
        type=str,
        default="first",
        choices=("first", "newest", "oldest"),
        help="Which copy to keep (default: first / alphabetical).",
    )
    delete_parser.set_defaults(func=cmd_delete)

    # export subcommand
    export_parser = subparsers.add_parser(
        "export",
        help="Export the duplicate file list to a file.",
        description="Scan for duplicates and write the results to a file.",
    )
    add_scan_options(export_parser)
    export_parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path (default: duplicates.txt). "
             "Extension decides format: .txt, .json, or .csv.",
    )
    export_parser.add_argument(
        "--keep",
        type=str,
        default="first",
        choices=("first", "newest", "oldest"),
        help="Which copy to mark as keep (default: first).",
    )
    export_parser.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    """Entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
