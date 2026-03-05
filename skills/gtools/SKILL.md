---
name: gtools
description: GTool Registry 模块化功能调用系统。使用 gtools 命令调用已注册的工具模块，支持语义匹配、配置管理和管道执行。触发场景：用户需要调用 gtools 工具模块、管理模块（创建/删除/更新）、执行批量任务管道、或查询模块信息。
---

# GTools Skill

## 核心命令

### 基础命令
```bash
gtools list                    # 列出所有已注册模块
gtools info <module>           # 查看模块详情（含 skill.md 状态）
gtools root                    # 输出 gtools 根目录路径
gtools <module> [args]         # 执行模块
gtools <module> start          # 执行模块启动脚本
gtools <module> --help         # 查看模块有哪些参数，意义是什么
```

### 模块管理
```bash
gtools create --skill <name>   # 创建新模块（带 SKILL.md 模板）
gtools remove <name>           # 删除模块
gtools remove --list           # 列出可删除的模块
```

### 管道执行
```bash
# 使用绝对路径（推荐，可移植）
gtools run --module-config $GTOOLS_ROOT/configs/<module>/default.json
gtools run --module-config <config> --option key=value

# 获取根路径
GTOOLS_ROOT=$(gtools root)
```

## 执行流程

1. **获取模块列表** → `gtools list`
2. **语义匹配** → 读取 `$(gtools root)/references/modules.md`，匹配关键词
3. **检查 skill** → `gtools info <module>` 查看 skill.md 状态
4. **执行模块** → 有 skill 则阅读后执行，无 skill 使用gtools <module> -h查询后询问具体参数

## 路径规范

**基础路径：** `$GTOOLS_ROOT` 或 `$(gtools root)`

所有相对路径都基于 `$GTOOLS_ROOT`：
- 语义映射表：`$GTOOLS_ROOT/skills/gtools/references/modules.md`
- 模块 skill：`$GTOOLS_ROOT/functions/<module>/SKILL.md`
- 配置文件：`$GTOOLS_ROOT/configs/<module>/default.json`

## 参考文档

- **模块语义映射表**：`references/modules.md` — 关键词匹配和模块路由

## 示例

### 示例 1：有 skill.md 的模块
```
用户："帮我备份 OpenClaw 记忆"

执行流程：
1. gtools list → 看到 backup_openclaw_memory
2. 读取 $(gtools root)/references/modules.md → 匹配"备份"、"OpenClaw"
3. gtools info backup_openclaw_memory → skill.md ✓ 是
4. 阅读 $(gtools root)/functions/backup_openclaw_memory/SKILL.md
5. 执行 gtools backup_openclaw_memory backup --name backup_20240304
```

### 示例 2：无 skill.md 的模块
```
用户："帮我执行一下批量数据回国"

执行流程：
1. gtools list → 看到 batch_landing
2. 读取 $(gtools root)/references/modules.md → 匹配"回国、数据回国、批量回国"
3. gtools info batch_landing → skill.md ✗ 否
4. 调用gtools batch_landing -h后看看有哪些参数，然后询问用户具体参数
```
