"""
OpenClaw Memory Backup Module

Backup and restore OpenClaw agent memories including:
- MEMORY.md (long-term memory)
- memory/*.md (daily notes)
- IDENTITY.md, USER.md, SOUL.md (agent identity)
- Other workspace configuration files
"""

from gtools.registry import FUNCTION, ARGS
import argparse
import os
import json
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


def get_logger(name=""):
    """Simple logger for the module."""
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s  %(levelname)s  %(name)s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = get_logger("backup_openclaw_memory")


class OpenClawMemoryBackup:
    """OpenClaw Memory Backup and Restore Manager"""
    
    ESSENTIAL_FILES = [
        "MEMORY.md",
        "IDENTITY.md",
        "USER.md",
        "SOUL.md",
        "AGENTS.md",
        "TOOLS.md",
        "HEARTBEAT.md",
    ]
    
    ESSENTIAL_DIRS = [
        "memory",
    ]
    
    def __init__(self, workspace_path: Optional[str] = None):
        if workspace_path is None:
            self.workspace_path = Path.home() / ".openclaw" / "workspace"
        else:
            self.workspace_path = Path(workspace_path)
        
        self.backup_root = Path.home() / ".openclaw" / "backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized backup manager for workspace: {self.workspace_path}")
    
    def _get_workspace_files(self) -> List[Path]:
        files_to_backup = []
        
        for file_name in self.ESSENTIAL_FILES:
            file_path = self.workspace_path / file_name
            if file_path.exists():
                files_to_backup.append(file_path)
            else:
                logger.debug(f"File not found (optional): {file_path}")
        
        for dir_name in self.ESSENTIAL_DIRS:
            dir_path = self.workspace_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        files_to_backup.append(file_path)
        
        return files_to_backup
    
    def backup(self, backup_name: Optional[str] = None, 
               include_all: bool = False) -> str:
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"openclaw_memory_{timestamp}"
        
        backup_path = self.backup_root / f"{backup_name}.tar.gz"
        
        if include_all:
            logger.info("Creating full workspace backup...")
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(self.workspace_path, arcname="workspace")
        else:
            logger.info("Creating memory-only backup...")
            files_to_backup = self._get_workspace_files()
            
            if not files_to_backup:
                logger.warning("No files found to backup!")
                metadata = {
                    "backup_type": "memory",
                    "timestamp": datetime.now().isoformat(),
                    "workspace_path": str(self.workspace_path),
                    "files_count": 0,
                }
                metadata_path = self.backup_root / f"{backup_name}_metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                return str(metadata_path)
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in files_to_backup:
                    try:
                        arcname = file_path.relative_to(self.workspace_path.parent)
                    except ValueError:
                        arcname = file_path.name
                    
                    tar.add(file_path, arcname=arcname)
                    logger.debug(f"Added to backup: {file_path}")
        
        metadata = {
            "backup_type": "full" if include_all else "memory",
            "timestamp": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "backup_file": str(backup_path),
            "files_count": len(files_to_backup) if not include_all else "all",
        }
        metadata_path = backup_path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Backup created: {backup_path}")
        
        return str(backup_path)
    
    def restore(self, backup_path: str, 
                workspace_path: Optional[str] = None,
                dry_run: bool = False) -> Dict[str, Any]:
        target_workspace = Path(workspace_path) if workspace_path else self.workspace_path
        target_workspace.mkdir(parents=True, exist_ok=True)
        
        backup_file = Path(backup_path)
        if backup_file.suffix == ".json":
            with open(backup_file, "r") as f:
                metadata = json.load(f)
            backup_file = Path(metadata.get("backup_file", ""))
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        logger.info(f"Restoring from backup: {backup_file}")
        
        result = {
            "success": False,
            "restored_files": [],
            "skipped_files": [],
            "errors": [],
        }
        
        if dry_run:
            logger.info("DRY RUN - No changes will be made")
            with tarfile.open(backup_file, "r:gz") as tar:
                members = tar.getmembers()
                result["files_to_restore"] = [m.name for m in members]
                result["success"] = True
                return result
        
        try:
            with tarfile.open(backup_file, "r:gz") as tar:
                members = tar.getmembers()
                
                for member in members:
                    if member.isdir():
                        continue
                    
                    member_path = Path(member.name)
                    
                    if member_path.parts[0] == "workspace":
                        relative_path = Path(*member_path.parts[1:])
                    else:
                        relative_path = member_path
                    
                    target_path = target_workspace / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        file_obj = tar.extractfile(member)
                        if file_obj:
                            with open(target_path, "wb") as f:
                                f.write(file_obj.read())
                            result["restored_files"].append(str(target_path))
                            logger.debug(f"Restored: {target_path}")
                    except Exception as e:
                        error_msg = f"Failed to restore {target_path}: {str(e)}"
                        result["errors"].append(error_msg)
                        logger.error(error_msg)
            
            result["success"] = len(result["errors"]) == 0
            logger.info(f"✓ Restore completed. Success: {result['success']}")
            logger.info(f"  Restored {len(result['restored_files'])} files")
            
        except Exception as e:
            error_msg = f"Failed to extract backup: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def list_backups(self) -> List[Dict[str, Any]]:
        backups = []
        
        for metadata_file in self.backup_root.glob("*.json"):
            if "_metadata.json" in metadata_file.name:
                continue
            
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                
                backup_file = Path(metadata.get("backup_file", ""))
                metadata["exists"] = backup_file.exists()
                metadata["size_mb"] = round(backup_file.stat().st_size / 1024 / 1024, 2) if backup_file.exists() else 0
                metadata["metadata_file"] = str(metadata_file)
                
                backups.append(metadata)
            except Exception as e:
                logger.error(f"Failed to read metadata {metadata_file}: {e}")
        
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return backups
    
    def delete_backup(self, backup_name: str) -> bool:
        backup_file = self.backup_root / f"{backup_name}.tar.gz"
        metadata_file = self.backup_root / f"{backup_name}.json"
        
        deleted = False
        
        if backup_file.exists():
            backup_file.unlink()
            logger.info(f"Deleted backup: {backup_file}")
            deleted = True
        
        if metadata_file.exists():
            metadata_file.unlink()
            logger.info(f"Deleted metadata: {metadata_file}")
            deleted = True
        
        return deleted


@FUNCTION.regist(module_name='backup_openclaw_memory')
def main(args: argparse.Namespace):
    """Main entry point for backup_openclaw_memory module."""
    print("🐱 OpenClaw Memory Backup & Restore")
    print("=" * 50)
    
    backup_mgr = OpenClawMemoryBackup(workspace_path=args.workspace)
    
    if args.command == "backup":
        print(f"\n📦 Creating backup...")
        backup_path = backup_mgr.backup(
            backup_name=args.name if args.name else None,
            include_all=args.full
        )
        print(f"✓ Backup created: {backup_path}")
        
        # Also print metadata file
        metadata_path = Path(backup_path).with_suffix(".json")
        if metadata_path.exists():
            print(f"  Metadata: {metadata_path}")
    
    elif args.command == "restore":
        print(f"\n🔄 Restoring from backup...")
        result = backup_mgr.restore(
            backup_path=args.backup_path,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            print("📋 Files to restore (DRY RUN):")
            for f in result.get("files_to_restore", []):
                print(f"    - {f}")
        else:
            if result["success"]:
                print(f"✓ Restore completed successfully!")
                print(f"  Restored {len(result['restored_files'])} files")
            else:
                print(f"✗ Restore failed with errors:")
                for error in result["errors"]:
                    print(f"    - {error}")
    
    elif args.command == "list":
        print(f"\n📋 Available backups:")
        backups = backup_mgr.list_backups()
        if not backups:
            print("  No backups found.")
        else:
            for i, backup in enumerate(backups, 1):
                exists = "✓" if backup.get("exists") else "✗"
                print(f"\n  [{i}] {exists} {Path(backup.get('backup_file', 'N/A')).name}")
                print(f"      Type: {backup.get('backup_type', 'N/A')}")
                print(f"      Time: {backup.get('timestamp', 'N/A')}")
                print(f"      Size: {backup.get('size_mb', 0)} MB")
    
    elif args.command == "delete":
        print(f"\n🗑️  Deleting backup: {args.backup_name}")
        if backup_mgr.delete_backup(args.backup_name):
            print(f"✓ Backup deleted successfully")
        else:
            print(f"✗ Backup not found")
    
    else:
        print("Unknown command. Use -h for help.")
    
    print("\n✅ Done!")


@ARGS.regist(module_name='backup_openclaw_memory')
def parse_args():
    """Parse arguments for backup_openclaw_memory module."""
    parser = argparse.ArgumentParser(
        description="🐱 OpenClaw Memory Backup & Restore - Backup your agent's soul and restore it on any device!"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a backup")
    backup_parser.add_argument("--name", "-n", type=str, help="Backup name")
    backup_parser.add_argument("--full", "-f", action="store_true", 
                               help="Backup entire workspace (not just memory)")
    backup_parser.add_argument("--workspace", "-w", type=str, default=None,
                               help="Workspace path (default: ~/.openclaw/workspace)")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup_path", type=str, help="Path to backup file")
    restore_parser.add_argument("--workspace", "-w", type=str, default=None,
                                help="Target workspace path")
    restore_parser.add_argument("--dry-run", "-d", action="store_true",
                                help="Show what would be restored without actually restoring")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all backups")
    list_parser.add_argument("--workspace", "-w", type=str, default=None,
                             help="Workspace path")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a backup")
    delete_parser.add_argument("backup_name", type=str, help="Backup name to delete")
    delete_parser.add_argument("--workspace", "-w", type=str, default=None,
                               help="Workspace path")
    
    # Default workspace for all commands
    parser.add_argument("--workspace", "-w", type=str, default=None,
                        help="Workspace path (default: ~/.openclaw/workspace)")
    
    return parser
