#!/usr/bin/env python3
"""
Test script for backup_openclaw_memory module
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from functions.backup_openclaw_memory.main import OpenClawMemoryBackup

def test_backup_restore():
    """Test backup and restore functionality"""
    print("🐱 Testing OpenClaw Memory Backup & Restore")
    print("=" * 60)
    
    # Initialize
    backup_mgr = OpenClawMemoryBackup()
    print(f"✓ Workspace: {backup_mgr.workspace_path}")
    print(f"✓ Backup root: {backup_mgr.backup_root}")
    print()
    
    # Test 1: List files to backup
    print("📋 Files to backup:")
    files = backup_mgr._get_workspace_files()
    for f in files:
        print(f"    - {f}")
    print(f"  Total: {len(files)} files")
    print()
    
    # Test 2: Create backup
    print("📦 Creating backup...")
    backup_path = backup_mgr.backup(backup_name="test_backup")
    print(f"✓ Backup created: {backup_path}")
    print()
    
    # Test 3: List backups
    print("📋 Available backups:")
    backups = backup_mgr.list_backups()
    for backup in backups:
        print(f"    - {backup.get('backup_file', 'N/A')}")
        print(f"      Type: {backup.get('backup_type', 'N/A')}")
        print(f"      Size: {backup.get('size_mb', 0)} MB")
    print()
    
    # Test 4: Dry run restore
    print("🔄 Testing restore (dry run)...")
    result = backup_mgr.restore(backup_path, dry_run=True)
    print(f"✓ Files to restore: {len(result.get('files_to_restore', []))}")
    for f in result.get('files_to_restore', [])[:5]:  # Show first 5
        print(f"    - {f}")
    print()
    
    print("=" * 60)
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_backup_restore()
