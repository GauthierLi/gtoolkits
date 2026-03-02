---
name: update
description: "模块配置更新工具 - 自动解析模块的 parse_args 函数并生成/更新配置文件，支持智能合并、SKILL.md 模板创建。使用当模块参数变更或需要生成配置时。"
homepage: ""
metadata: { "openclaw": { "emoji": "🔄", "requires": { "bins": ["python3"] } } }
---

# update 模块

## 使用时机

✅ **使用场景：**
- 模块添加了新参数，需要同步更新配置文件时
- 创建新模块后生成初始配置文件
- 模块缺少 SKILL.md，需要自动创建模板
- 查看模块的参数定义和配置结构

❌ **不使用场景：**
- 手动编辑配置文件（会覆盖手动修改的内容）
- 修改模块代码逻辑（这是配置工具，不是代码编辑器）
- 删除模块配置（应使用 `remove` 模块）

## 功能说明

### 主要功能

1. **自动解析参数**：使用 AST 解析 `parse_args()` 函数，提取所有参数定义
2. **生成配置文件**：创建或更新 `configs/<module_name>/default.json`
3. **智能合并**：保留现有配置中的自定义值，只更新新增参数
4. **SKILL.md 创建**：
   - `--skill`：手动创建 SKILL.md 模板
   - `--auto-skill`：自动检测，如果不存在则创建

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 是 | 要更新的模块名称 |
| `--force` / `-f` | bool | 否 | 强制覆盖现有配置（不合并） |
| `--verbose` / `-v` | bool | 否 | 显示详细信息 |
| `--skill` / `-s` | bool | 否 | 手动创建 SKILL.md 模板 |
| `--auto-skill` | bool | 否 | 自动检测并创建 SKILL.md（如果不存在） |

### 输出

- **配置文件**：`configs/<module_name>/default.json`
- **SKILL.md**：`functions/<module_name>/SKILL.md`（如果指定）
- **配置摘要**：显示更新后的配置结构

## 命令/用法

### 基本用法

```bash
# 更新模块配置（智能合并）
gtools update my_module

# 强制覆盖现有配置
gtools update my_module --force

# 显示详细信息
gtools update my_module -v

# 更新配置并创建 SKILL.md
gtools update my_module --skill

# 自动检测，如果缺少 SKILL.md 就创建
gtools update my_module --auto-skill

# 组合使用
gtools update my_module --verbose --skill
```

### 使用示例

```bash
# 1. 创建新模块
gtools create data_processor

# 2. 编辑 main.py 添加参数
# ... 编辑 functions/data_processor/main.py ...

# 3. 生成配置文件
gtools update data_processor

# 4. 创建 SKILL.md 模板
gtools update data_processor --auto-skill

# 输出：
# 🔄 开始更新模块 'data_processor' 的配置...
# 📄 发现已存在的配置文件，将进行智能合并...
# ✅ 配置文件已更新：/path/to/configs/data_processor/default.json
# 📦 检测到模块缺少 SKILL.md，正在创建技能模板...
# ✅ 创建技能包模板：/path/to/functions/data_processor/SKILL.md
```

## 配置示例

### 生成的配置文件结构

```json
{
  "_positional_args": {
    "module_name": "data_processor"
  },
  "input_file": "input.csv",
  "output_dir": "/tmp/output",
  "batch_size": 32,
  "verbose": false
}
```

### 使用配置文件运行

```bash
# 使用默认配置
gtools run --module-config configs/data_processor/default.json

# 覆盖部分参数
gtools run --module-config configs/data_processor/default.json --batch_size 64
```

## 注意事项

- **AST 解析**：使用 Python AST 解析 `parse_args()` 函数，需要规范的 argparse 代码
- **智能合并**：默认保留现有配置值，只添加新参数；用 `--force` 可完全覆盖
- **SKILL.md 模板**：创建后需要手动完善功能描述、使用场景等内容
- **模块检查**：会先检查模块是否存在，不存在会报错

## 相关文件

- 主模块：`functions/update/main.py`
- 配置文件：`configs/update/default.json`
- 参考模板：`functions/create/reference/SKILL.md`
