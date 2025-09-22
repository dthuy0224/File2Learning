#!/usr/bin/env python3
"""
Cleanup script to remove redundant files and folders
"""

import os
import shutil
from pathlib import Path

def cleanup_redundant_files():
    """Remove redundant files and folders"""

    print("🧹 CLEANUP REDUNDANT FILES")
    print("=" * 50)

    backend_dir = Path(".")

    # Files to remove
    files_to_remove = [
        "test_db.py",
        "test_crud.py",
        "test_migrations.py",
        "database_test_report.py"
    ]

    # Folders to remove
    folders_to_remove = [
        "scripts/uploads",  # Empty uploads folder
    ]

    # Files to remove in scripts
    scripts_files_to_remove = [
        "scripts/app.db"  # Empty database file
    ]

    print("📁 Files to remove:")
    for file_path in files_to_remove:
        if (backend_dir / file_path).exists():
            print(f"  ❌ {file_path}")
        else:
            print(f"  ✅ {file_path} - Already removed")

    print("\n📂 Folders to remove:")
    for folder_path in folders_to_remove:
        if (backend_dir / folder_path).exists():
            print(f"  ❌ {folder_path}")
        else:
            print(f"  ✅ {folder_path} - Already removed")

    print("\n📄 Files in scripts to remove:")
    for file_path in scripts_files_to_remove:
        if (backend_dir / file_path).exists():
            print(f"  ❌ {file_path}")
        else:
            print(f"  ✅ {file_path} - Already removed")

    # Confirm cleanup
    print("\n⚠️ CONFIRMATION REQUIRED")
    print("-" * 30)
    print("The following will be removed:")
    print(f"  - {len(files_to_remove)} test files")
    print(f"  - {len(folders_to_remove)} empty folders")
    print(f"  - {len(scripts_files_to_remove)} duplicate files")

    confirm = input("\nProceed with cleanup? (y/N): ").lower().strip()

    if confirm not in ['y', 'yes']:
        print("❌ Cleanup cancelled")
        return

    # Remove files
    print("\n🗑️ Removing files...")
    for file_path in files_to_remove:
        full_path = backend_dir / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✅ Removed {file_path}")
            except Exception as e:
                print(f"  ❌ Failed to remove {file_path}: {e}")

    # Remove folders
    for folder_path in folders_to_remove:
        full_path = backend_dir / folder_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"  ✅ Removed {folder_path}")
            except Exception as e:
                print(f"  ❌ Failed to remove {folder_path}: {e}")

    # Remove files in scripts
    for file_path in scripts_files_to_remove:
        full_path = backend_dir / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✅ Removed {file_path}")
            except Exception as e:
                print(f"  ❌ Failed to remove {file_path}: {e}")

    print("\n✅ Cleanup completed!")

    # Show remaining files
    print("\n📋 Remaining files:")
    remaining_files = []
    for file_path in files_to_remove + scripts_files_to_remove:
        if (backend_dir / file_path).exists():
            remaining_files.append(file_path)

    if remaining_files:
        print("  ⚠️ Some files could not be removed:")
        for file_path in remaining_files:
            print(f"    - {file_path}")
    else:
        print("  ✅ All redundant files removed successfully")

if __name__ == "__main__":
    cleanup_redundant_files()
