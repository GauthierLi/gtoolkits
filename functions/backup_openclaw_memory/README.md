# backup_openclaw_memory

🐱 **OpenClaw Memory Backup & Restore** - 备份你的代理灵魂，在任何设备上重生！

## 功能

- 备份 OpenClaw 代理的核心记忆文件：
  - `MEMORY.md` - 长期记忆
  - `memory/*.md` - 每日笔记
  - `IDENTITY.md`, `USER.md`, `SOUL.md` - 代理身份配置
  - `AGENTS.md`, `TOOLS.md`, `HEARTBEAT.md` - 工作区配置
- 支持完整工作区备份或仅记忆文件备份
- 一键恢复所有记忆
- 备份列表和管理
- 跨设备迁移支持

## 使用方法

### 通过 gtools 运行（推荐）

```bash
# 创建备份
gtools backup_openclaw_memory backup

# 自定义备份名称
gtools backup_openclaw_memory backup --name my_backup_2024

# 备份整个工作区（不只是记忆文件）
gtools backup_openclaw_memory backup --full

# 指定工作区路径
gtools backup_openclaw_memory backup --workspace /path/to/workspace

# 列出所有备份
gtools backup_openclaw_memory list

# 恢复备份
gtools backup_openclaw_memory restore /path/to/backup.tar.gz

# 预览恢复内容（不实际恢复）
gtools backup_openclaw_memory restore /path/to/backup.tar.gz --dry-run

# 恢复到指定工作区
gtools backup_openclaw_memory restore /path/to/backup.tar.gz --workspace /new/path

# 删除备份
gtools backup_openclaw_memory delete backup_name
```

### 使用启动脚本

```bash
# 使用 start.sh
gtools backup_openclaw_memory start backup --name my_backup
gtools backup_openclaw_memory start list
gtools backup_openclaw_memory start restore /path/to/backup.tar.gz
```

### Python API

```python
import sys
sys.path.insert(0, '/path/to/gtoolkits')

from functions.backup_openclaw_memory.main import OpenClawMemoryBackup

backup_mgr = OpenClawMemoryBackup()

# 创建备份
backup_path = backup_mgr.backup(backup_name="my_backup")

# 恢复备份
result = backup_mgr.restore(backup_path)

# 列出所有备份
backups = backup_mgr.list_backups()

# 删除备份
backup_mgr.delete_backup("my_backup")
```

## 备份位置

备份文件默认存储在：`~/.openclaw/backups/`

每个备份包含：
- `.tar.gz` - 压缩的备份文件
- `.json` - 备份元数据（时间戳、文件列表等）

## 使用场景

### 换设备迁移

1. **在旧设备上创建备份：**
   ```bash
   gtools backup_openclaw_memory backup --name migration_backup
   ```

2. **复制备份文件到新设备：**
   ```bash
   scp ~/.openclaw/backups/migration_backup.tar.gz new-device:~/.openclaw/backups/
   scp ~/.openclaw/backups/migration_backup.tar.json new-device:~/.openclaw/backups/
   ```

3. **在新设备上恢复：**
   ```bash
   gtools backup_openclaw_memory restore ~/.openclaw/backups/migration_backup.tar.gz
   ```

### 定期备份

```bash
# 每周备份（添加到 crontab）
0 0 * * 0 cd /path/to/gtoolkits && gtools backup_openclaw_memory backup --name weekly_$(date +\%Y\%m\%d)
```

## 文件结构

```
functions/backup_openclaw_memory/
├── main.py                     # gtools 模块入口（含注册装饰器）
├── start.sh                    # 启动脚本
├── test_backup.py              # 测试脚本
└── README.md                   # 本文档

configs/backup_openclaw_memory/
└── default.json                # 默认配置
```

## 注意事项

- 备份不包含 OpenClaw 的 API keys 和认证信息（安全考虑）
- 恢复时会覆盖目标工作区的现有文件
- 建议恢复前先用 `--dry-run` 预览
- 跨设备迁移时需要确保新设备已安装 OpenClaw 和 gtoolkits

## 测试

```bash
cd /path/to/gtoolkits
python3 functions/backup_openclaw_memory/test_backup.py
```

## 作者

Gauthier Li - 为喵了个咪 (GausMiao) 打造的转世系统 🐱
