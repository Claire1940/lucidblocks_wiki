#!/usr/bin/env python3
"""
Remove _init Suffix from MDX Files

This script renames all *_init.mdx files to remove the _init suffix.
Example: pixel-blade-codes_init.mdx -> pixel-blade-codes.mdx

Usage:
    python tools/articles/remove-init-suffix.py [--dry-run] [--force]
"""

import os
import sys
import argparse
from pathlib import Path


class FilenameRemover:
    def __init__(self, base_dir: str = "src/content/", dry_run: bool = False, force: bool = False):
        """
        Initialize the filename remover.

        Args:
            base_dir: Base directory to search for files
            dry_run: If True, only show what would be renamed without actually doing it
            force: If True, overwrite existing files
        """
        self.base_dir = base_dir
        self.dry_run = dry_run
        self.force = force
        self.stats = {
            'total_found': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }

    def find_init_files(self):
        """
        Find all files ending with _init.mdx.

        Returns:
            List of Path objects
        """
        base_path = Path(self.base_dir)
        if not base_path.exists():
            print(f"❌ Error: Directory {self.base_dir} does not exist")
            return []

        # Find all *_init.mdx files recursively
        init_files = list(base_path.rglob("*_init.mdx"))
        return init_files

    def rename_file(self, file_path: Path) -> bool:
        """
        Rename a single file to remove _init suffix.

        Args:
            file_path: Path to the file to rename

        Returns:
            True if successful, False otherwise
        """
        # Generate new filename
        old_name = file_path.name
        new_name = old_name.replace('_init.mdx', '.mdx')
        new_path = file_path.parent / new_name

        # Check if target already exists
        if new_path.exists() and not self.force:
            print(f"⚠️  Skipping {old_name} -> {new_name} (target exists, use --force to overwrite)")
            self.stats['skipped'] += 1
            return False

        # Dry run mode
        if self.dry_run:
            print(f"🔍 Would rename: {file_path.relative_to(self.base_dir)} -> {new_name}")
            self.stats['renamed'] += 1
            return True

        # Actually rename
        try:
            file_path.rename(new_path)
            print(f"✅ Renamed: {file_path.relative_to(self.base_dir)} -> {new_name}")
            self.stats['renamed'] += 1
            return True
        except Exception as e:
            print(f"❌ Error renaming {old_name}: {str(e)}")
            self.stats['errors'] += 1
            return False

    def process_all(self):
        """Process all _init.mdx files."""
        print("=" * 60)
        print("🔧 MDX FILENAME CLEANUP - REMOVE _init SUFFIX")
        print("=" * 60)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified\n")

        # Find all files
        print(f"📂 Searching for *_init.mdx files in {self.base_dir}...\n")
        init_files = self.find_init_files()

        if not init_files:
            print("ℹ️  No *_init.mdx files found")
            return

        self.stats['total_found'] = len(init_files)
        print(f"📝 Found {len(init_files)} files to process\n")

        # Process each file
        for file_path in sorted(init_files):
            self.rename_file(file_path)

        # Print statistics
        self.print_stats()

    def print_stats(self):
        """Print statistics."""
        print("\n" + "=" * 60)
        print("📊 CLEANUP STATISTICS")
        print("=" * 60)
        print(f"Total Files Found:    {self.stats['total_found']}")
        print(f"Successfully Renamed: {self.stats['renamed']} ✅")
        print(f"Skipped (exists):     {self.stats['skipped']} ⚠️")
        print(f"Errors:               {self.stats['errors']} ❌")

        if self.stats['total_found'] > 0:
            success_rate = round(self.stats['renamed'] / self.stats['total_found'] * 100, 2)
            print(f"Success Rate:         {success_rate}%")

        print("=" * 60)

        if self.dry_run:
            print("\nℹ️  This was a dry run. Run without --dry-run to actually rename files.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Remove _init suffix from MDX files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be renamed (recommended first)
  python tools/articles/remove-init-suffix.py --dry-run

  # Actually rename files
  python tools/articles/remove-init-suffix.py

  # Force overwrite if target files exist
  python tools/articles/remove-init-suffix.py --force
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually renaming files'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite target files if they already exist'
    )

    parser.add_argument(
        '--base-dir',
        type=str,
        default='src/content/',
        help='Base directory to search for files (default: src/content/)'
    )

    args = parser.parse_args()

    # Create remover and process files
    remover = FilenameRemover(
        base_dir=args.base_dir,
        dry_run=args.dry_run,
        force=args.force
    )

    try:
        remover.process_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
