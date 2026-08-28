#!/usr/bin/env python3
"""
Demo script for the Duplicate File Cleaner.

This script creates a temporary directory with some duplicate files,
then demonstrates how to use the duplicate cleaner as a library
by importing functions directly from main.py.

Run it from the project root:

    python examples/demo.py

The script creates and cleans up a temporary directory, so it is safe
to run and will not touch any of your real files.
"""

import os
import shutil
import sys
import tempfile

# Add the project root to the path so we can import main.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    delete_duplicates,
    export_duplicates,
    format_size,
    hash_file,
    print_duplicates,
    reorder_by_keep_strategy,
    scan_by_content,
    scan_by_name,
)


# ---------------------------------------------------------------------------
# Helpers to create test files
# ---------------------------------------------------------------------------

def create_file(filepath: str, content: str) -> None:
    """Write ``content`` to ``filepath``, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def make_test_directory() -> str:
    """Create a temporary directory with known duplicate files.

    Layout:
        demo_dir/
            docs/
                report.txt        <- "Hello World" (original)
                report_copy.txt   <- "Hello World" (duplicate content)
            photos/
                sunset.jpg        <- "IMGDATA1" (duplicate content)
                backup/
                    sunset.jpg    <- "IMGDATA1" (duplicate content + name)
                    vacation.jpg  <- "IMGDATA2" (unique)
            notes.txt             <- "Unique note" (no duplicates)

    Returns:
        The path to the temporary directory.
    """
    tmp = tempfile.mkdtemp(prefix="dup_cleaner_demo_")

    # Two identical text files (content duplicates).
    create_file(os.path.join(tmp, "docs", "report.txt"), "Hello World\n")
    create_file(os.path.join(tmp, "docs", "report_copy.txt"), "Hello World\n")

    # Two identical "image" files, one with a duplicate name.
    create_file(os.path.join(tmp, "photos", "sunset.jpg"), "IMGDATA1")
    create_file(
        os.path.join(tmp, "photos", "backup", "sunset.jpg"), "IMGDATA1"
    )

    # A unique file (no duplicates at all).
    create_file(os.path.join(tmp, "photos", "vacation.jpg"), "IMGDATA2")

    # Another unique file.
    create_file(os.path.join(tmp, "notes.txt"), "Unique note\n")

    return tmp


# ---------------------------------------------------------------------------
# Demo sections
# ---------------------------------------------------------------------------

def demo_hash() -> None:
    """Show file hashing."""
    print("=" * 50)
    print("Demo 1: File Content Hashing")
    print("=" * 50)

    tmp = make_test_directory()
    filepath = os.path.join(tmp, "docs", "report.txt")
    digest = hash_file(filepath, algorithm="sha256")
    size = os.path.getsize(filepath)

    print(f"  File:       {filepath}")
    print(f"  Size:       {format_size(size)}")
    print(f"  SHA-256:    {digest}")
    print()

    # Clean up.
    shutil.rmtree(tmp)


def demo_scan_content() -> None:
    """Scan for content duplicates."""
    print("=" * 50)
    print("Demo 2: Scan by Content Hash")
    print("=" * 50)

    tmp = make_test_directory()
    duplicates = scan_by_content(tmp)
    print_duplicates(duplicates, mode="content")
    shutil.rmtree(tmp)


def demo_scan_by_name() -> None:
    """Scan for filename duplicates."""
    print()
    print("=" * 50)
    print("Demo 3: Scan by Filename")
    print("=" * 50)

    tmp = make_test_directory()
    duplicates = scan_by_name(tmp)
    print_duplicates(duplicates, mode="name")
    shutil.rmtree(tmp)


def demo_dry_run_delete() -> None:
    """Preview deletion without actually deleting."""
    print()
    print("=" * 50)
    print("Demo 4: Dry-Run Delete")
    print("=" * 50)

    tmp = make_test_directory()
    duplicates = scan_by_content(tmp)
    duplicates = reorder_by_keep_strategy(duplicates, keep="first")

    print_duplicates(duplicates, mode="content")
    print("\n--- DRY RUN (no files will be deleted) ---")
    deleted, freed = delete_duplicates(duplicates, dry_run=True)
    print(f"\nWould delete {deleted} file(s), freeing {format_size(freed)}.")
    shutil.rmtree(tmp)


def demo_export() -> None:
    """Export duplicate lists to different formats."""
    print()
    print("=" * 50)
    print("Demo 5: Export to JSON")
    print("=" * 50)

    tmp = make_test_directory()
    duplicates = scan_by_content(tmp)

    output_file = os.path.join(tmp, "duplicates.json")
    export_duplicates(duplicates, output_file, fmt="json")

    # Show a snippet of the exported file.
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"\n  Exported file ({len(content)} bytes):")
    for line in content.splitlines()[:6]:
        print(f"    {line}")
    print("    ...")
    shutil.rmtree(tmp)


def main() -> None:
    """Run all demos."""
    print()
    print("*" * 50)
    print("  Duplicate File Cleaner - Demo")
    print("*" * 50)

    demo_hash()
    demo_scan_content()
    demo_scan_by_name()
    demo_dry_run_delete()
    demo_export()

    print()
    print("*" * 50)
    print("  Demo complete!")
    print("*" * 50)
    print()
    print("Try the CLI directly:")
    print("  python main.py scan /path/to/dir")
    print("  python main.py scan /path/to/dir --by-name")
    print("  python main.py delete /path/to/dir --dry-run")
    print("  python main.py export /path/to/dir -o dups.json")
    print()


if __name__ == "__main__":
    main()
