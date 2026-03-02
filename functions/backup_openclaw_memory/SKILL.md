---
name: backup_openclaw_memory
description: "OpenClaw 记忆备份与恢复 - 备份/恢复/管理 OpenClaw 代理的核心记忆文件（MEMORY.md、每日笔记、身份配置）。使用当需要迁移数据、备份记忆或跨设备同步时。"
homepage: ""
metadata: { "openclaw": { "emoji": "💾", "requires": { "bins": ["python3"] } } }
---

# backup_openclaw_memory 模块

## 使用时机

✅ **使用场景：**
- 需要备份 OpenClaw 代理的记忆和配置时
- 跨设备迁移代理（换电脑、重装系统）
- 定期备份防止数据丢失
- 恢复之前的记忆状态
- 查看备份历史和管理备份文件

❌ **不使用场景：**
- 实时同步（这是手动备份工具，不是自动同步）
- 备份 API keys 和认证信息（出于安全考虑不包含）
- 备份整个系统（仅针对 OpenClaw workspace）

## 功能说明

### 主要功能

1. **备份**：创建记忆文件的压缩备份（.tar.gz + .json 元数据）
2. **恢复**：从备份文件恢复记忆到工作区
3. **列表**：查看所有可用的备份
4. **删除**：管理删除旧的备份
5. **预览**：恢复前用 `--dry-run` 预览内容

### 备份内容

**核心文件：**
- `MEMORY.md` - 长期记忆
- `memory/*.md` - 每日笔记
- `IDENTITY.md`, `USER.md`, `SOUL.md` - 代理身份
- `AGENTS.md`, `TOOLS.md`, `HEARTBEAT.md` - 工作区配置

**备份位置：** `~/.openclaw/backups/`

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `backup` | command | 子命令 | 创建备份 |
| `restore` | command | 子命令 | 恢复备份 |
| `list` | command | 子命令 | 列出所有备份 |
| `delete` | command | 子命令 | 删除指定备份 |
| `--name` | string | 否 | 备份名称（默认：时间戳） |
| `--full` | bool | 否 | 备份整个工作区（不仅是记忆文件） |
| `--workspace` | string | 否 | 指定工作区路径（默认：~/.openclaw/workspace） |
| `--dry-run` | bool | 否 | 预览恢复内容，不实际执行 |

## 命令/用法

### 基本用法

```bash
# 创建备份（使用时间戳命名）
gtools backup_openclaw_memory backup

# 自定义备份名称
gtools backup_openclaw_memory backup --name my_backup_2024

# 备份整个工作区
gtools backup_openclaw_memory backup --full

# 列出所有备份
gtools backup_openclaw_memory list

# 恢复备份
gtools backup_openclaw_memory restore ~/.openclaw/backups/openclaw_memory_20240302_173500.tar.gz

# 预览恢复内容（不实际恢复）
gtools backup_openclaw_memory restore backup.tar.gz --dry-run

# 恢复到指定工作区
gtools backup_openclaw_memory restore backup.tar.gz --workspace /new/path

# 删除备份
gtools backup_openclaw_memory delete backup_name
```

### 跨设备迁移

```bash
# 1. 旧设备创建备份
gtools backup_openclaw_memory backup --name migration

# 2. 复制备份文件到新设备
scp ~/.openclaw/backups/migration.tar.gz new-device:~/.openclaw/backups/
scp ~/.openclaw/backups/migration.tar.json new-device:~/.openclaw/backups/

# 3. 新设备恢复
gtools backup_openclaw_memory restore ~/.openclaw/backups/migration.tar.gz
```

### 定期备份（Cron）

```bash
# 添加到 crontab，每周日午夜备份
0 0 * * 0 cd /path/to/gtoolkits && gtools backup_openclaw_memory backup --name weekly_$(date +\%Y\%m\%d)
```

## 配置示例

```json
{
  "_positional_args": {
    "command": "backup"
  },
  "name": "daily_backup",
  "full": false,
  "workspace": "/home/user/.openclaw/workspace"
}
```

## 注意事项

- **备份不包含**：API keys、认证信息（安全考虑）
- **恢复会覆盖**：目标工作区的现有文件，建议先用 `--dry-run` 预览
- **备份格式**：`.tar.gz`（压缩文件）+ `.json`（元数据）
- **默认路径**：
  - 工作区：`~/.openclaw/workspace`
  - 备份：`~/.openclaw/backups/`

## 相关文件

- 主模块：`functions/backup_openclaw_memory/main.py`
- 启动脚本：`functions/backup_openclaw_memory/start.sh`
- 测试脚本：`functions/backup_openclaw_memory/test_backup.py`
- 配置文件：`configs/backup_openclaw_memory/default.json`
