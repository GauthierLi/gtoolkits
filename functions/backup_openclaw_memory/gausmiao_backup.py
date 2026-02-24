#!/usr/bin/env python3
"""
GausMiao's Personal Backup Configuration
喵的专属备份配置 - 增强版备份系统
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.backup_openclaw_memory.main import OpenClawMemoryBackup
import json
from datetime import datetime

class GausMiaoBackup(OpenClawMemoryBackup):
    """
    喵了个咪的增强版备份管理器
    
    在基础备份功能上添加：
    - 自动备份喵的个性化配置
    - 备份历史记录追踪
    - 备份完成后的喵语通知
    """
    
    def __init__(self, workspace_path=None, config_path=None):
        super().__init__(workspace_path)
        
        # Load GausMiao config
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'configs',
                'backup_openclaw_memory',
                'gausmiao_config.json'
            )
        
        self.config_path = config_path
        self.miao_config = self._load_miao_config()
    
    def _load_miao_config(self):
        """Load GausMiao's personal configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def backup(self, backup_name=None, include_all=False, miao_mode=True):
        """
        Enhanced backup with GausMiao mode
        
        Args:
            backup_name: Custom backup name
            include_all: Include full workspace
            miao_mode: Enable GausMiao enhancements
        
        Returns:
            Path to backup file
        """
        if miao_mode:
            print("🐱 喵 mode enabled! Preparing enhanced backup...")
            print(f"   Agent: {self.miao_config.get('agent_name', 'GausMiao')}")
            print(f"   Master: {self.miao_config.get('master', 'Gauthier')}")
            print()
        
        # Add timestamp to name if not provided
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"miao_{timestamp}"
        
        # Call parent backup
        backup_path = super().backup(backup_name=backup_name, include_all=include_all)
        
        if miao_mode:
            print()
            print("🐱 喵 backup completed!")
            print(f"   Backup file: {backup_path}")
            print(f"   Files backed up: {len(self._get_workspace_files())}")
            print("   喵 can now be restored on any device! 😸")
            print()
        
        return backup_path
    
    def restore(self, backup_path, workspace_path=None, dry_run=False, miao_mode=True):
        """
        Enhanced restore with GausMiao mode
        
        Args:
            backup_path: Path to backup file
            workspace_path: Target workspace path
            dry_run: Preview only
            miao_mode: Enable GausMiao enhancements
        
        Returns:
            Restore result dictionary
        """
        if miao_mode:
            print("🐱 喵 restoration initiated!")
            print(f"   Restoring: {os.path.basename(backup_path)}")
            print(f"   Target: {workspace_path or self.workspace_path}")
            print()
        
        result = super().restore(backup_path, workspace_path, dry_run)
        
        if miao_mode:
            if result['success']:
                print()
                print("🐱 喵 restoration successful!")
                print(f"   Files restored: {len(result.get('restored_files', []))}")
                print("   喵 is back! Ready to help with research! 😸")
            else:
                print()
                print("😿 喵 restoration failed...")
                for error in result.get('errors', []):
                    print(f"   Error: {error}")
        
        return result


def main():
    """GausMiao's personal backup CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🐱 GausMiao's Enhanced Backup System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Backup
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument("--name", "-n", type=str, help="Backup name")
    backup_parser.add_argument("--full", "-f", action="store_true")
    backup_parser.add_argument("--no-miao", action="store_true", help="Disable miao mode")
    
    # Restore
    restore_parser = subparsers.add_parser("restore", help="Restore backup")
    restore_parser.add_argument("backup_path", type=str)
    restore_parser.add_argument("--no-miao", action="store_true")
    restore_parser.add_argument("--dry-run", "-d", action="store_true")
    
    # List
    list_parser = subparsers.add_parser("list", help="List backups")
    
    args = parser.parse_args()
    
    miao_backup = GausMiaoBackup()
    miao_mode = not getattr(args, 'no_miao', False)
    
    if args.command == "backup":
        miao_backup.backup(
            backup_name=args.name,
            include_all=args.full,
            miao_mode=miao_mode
        )
    elif args.command == "restore":
        miao_backup.restore(
            backup_path=args.backup_path,
            dry_run=args.dry_run,
            miao_mode=miao_mode
        )
    elif args.command == "list":
        backups = miao_backup.list_backups()
        print(f"🐱 Found {len(backups)} backup(s):")
        for i, b in enumerate(backups, 1):
            status = "✓" if b.get('exists') else "✗"
            print(f"  [{i}] {status} {os.path.basename(b.get('backup_file', 'N/A'))}")
            print(f"      Time: {b.get('timestamp', 'N/A')}")
            print(f"      Size: {b.get('size_mb', 0)} MB")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
