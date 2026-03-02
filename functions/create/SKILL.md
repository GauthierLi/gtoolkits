---
name: create
description: "模块创建工具 - 自动生成新的 gtoolkits 模块模板（main.py、配置文件、启动脚本、SKILL.md）。使用当需要快速创建新模块/技能包时。"
homepage: ""
metadata: { "openclaw": { "emoji": "🆕", "requires": { "bins": ["python3"] } } }
---

# create 模块

## 使用时机

✅ **使用场景：**
- 需要创建新的 gtoolkits 模块时
- 快速生成模块模板（main.py、配置、启动脚本）
- 同时创建 OpenClaw 技能包（SKILL.md）
- 标准化模块结构，遵循项目规范

❌ **不使用场景：**
- 手动编写模块（不需要模板时）
- 修改现有模块（应使用 `update` 模块）
- 删除模块（应使用 `remove` 模块）

## 功能说明

### 主要功能

1. **创建模块目录**：在 `functions/<module_name>/` 下创建新目录
2. **生成模板文件**：
   - `main.py` - 模块主入口（含注册装饰器）
   - `start.sh` - 启动脚本
   - `default.json` - 配置文件（在 `configs/<module_name>/`）
   - `SKILL.md` - OpenClaw 技能包文档（可选）
3. **占位符替换**：自动将模板中的 `{MODULE_NAME}` 替换为实际模块名

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 是 | 新模块的名称 |
| `--skill` / `-s` | bool | 否 | 同时创建 SKILL.md 技能包模板 |

### 输出

- **模块目录**：`functions/<module_name>/`
- **配置目录**：`configs/<module_name>/`
- **控制台输出**：创建进度和文件路径信息

## 命令/用法

### 基本用法

```bash
# 创建新模块（基础模板）
gtools create my_module

# 创建模块并生成 SKILL.md
gtools create my_module --skill

# 简写
gtools create my_module -s
```

### 创建后的文件结构

```
gtoolkits/
├── functions/my_module/
│   ├── main.py              # 模块主入口
│   └── start.sh             # 启动脚本
└── configs/my_module/
    └── default.json         # 默认配置
```

如果加上 `--skill`：
```
functions/my_module/
├── main.py
├── start.sh
└── SKILL.md                 # OpenClaw 技能包文档
```

## 配置示例

```json
{
  "_positional_args": {
    "module_name": "data_processor"
  },
  "skill": true
}
```

## 模板内容

### main.py 模板

```python
"""
{MODULE_NAME} 模块：模块功能描述
用法：gtools {MODULE_NAME} [参数]
"""

import argparse
from gtools.registry import ARGS, FUNCTION


@FUNCTION.regist(module_name="{MODULE_NAME}")
def main(args: argparse.Namespace):
    """主函数：处理模块逻辑"""
    # TODO: 实现你的功能
    pass


@ARGS.regist(module_name="{MODULE_NAME}")
def parse_args():
    """参数解析函数"""
    parser = argparse.ArgumentParser(description="{MODULE_NAME} 功能描述")
    # TODO: 添加参数
    return parser
```

## 注意事项

- **模块命名**：使用小写字母和下划线（如 `my_module`）
- **检查重复**：如果模块已存在会报错并退出
- **系统保留模块**：不能创建与现有模块同名的模块
- **SKILL.md**：创建后需要根据实际功能手动完善内容

## 相关文件

- 主模块：`functions/create/main.py`
- 模板目录：`functions/create/reference/`
  - `main.py` - main.py 模板
  - `start.sh` - 启动脚本模板
  - `default.json` - 配置文件模板
  - `SKILL.md` - 技能包模板
