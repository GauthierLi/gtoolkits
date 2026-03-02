---
name: remove
description: "模块删除工具 - 安全移除 gtoolkits 模块和配置文件，支持列出可删除模块、强制删除、确认保护。使用当需要清理不需要的模块时。"
homepage: ""
metadata: { "openclaw": { "emoji": "🗑️", "requires": { "bins": ["python3"] } } }
---

# remove 模块

## 使用时机

✅ **使用场景：**
- 需要删除不再使用的 gtoolkits 模块时
- 清理实验性模块和配置文件
- 查看哪些模块可以被安全删除
- 批量清理开发过程中的临时模块

❌ **不使用场景：**
- 删除系统核心模块（会自动阻止）
- 删除外部 OpenClaw 技能（应使用 clawhub 或手动删除）
- 临时禁用模块（可以通过不调用来实现，无需删除）

## 功能说明

### 主要功能

1. **删除模块**：移除 `functions/<module_name>/` 目录
2. **删除配置**：移除 `configs/<module_name>/` 目录
3. **列出可删除模块**：显示所有非系统保留的模块
4. **安全保护**：
   - 系统保留模块不能删除
   - 删除前需要确认（可用 `--force` 跳过）
   - 检查模块是否存在

### 系统保留模块

以下模块不能被删除：
- `create` - 模块创建工具
- `remove` - 模块删除工具（自己不能删除自己）
- `test_module` - 测试模块
- `calculator` - 计算器
- `update` - 模块更新工具

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module_name` | string | 条件 | 要删除的模块名称（与 `--list` 互斥） |
| `--list` | bool | 否 | 列出所有可删除的模块 |
| `--force` / `-f` | bool | 否 | 跳过确认提示，强制删除 |
| `--backup` | bool | 否 | 删除前创建备份（预留功能） |

### 输出

- **删除结果**：成功/失败信息
- **已删除项目**：列出删除的目录路径
- **可删除列表**：使用 `--list` 时显示所有可删除模块

## 命令/用法

### 基本用法

```bash
# 删除指定模块（会提示确认）
gtools remove my_module

# 强制删除（不提示确认）
gtools remove my_module --force

# 简写
gtools remove my_module -f

# 列出所有可删除的模块
gtools remove --list
```

### 删除流程示例

```bash
# 1. 先查看可删除的模块
gtools remove --list

# 2. 删除不需要的模块
gtools remove experimental_feature

# 输出：
# 🗑️  准备删除模块：experimental_feature
# 📂 模块目录：/path/to/gtoolkits/functions/experimental_feature
# ⚙️  配置目录：/path/to/gtoolkits/configs/experimental_feature
#
# ⚠️  警告：此操作不可逆！
# 确认删除模块 'experimental_feature' 吗？[y/N]: y
#
# ✅ 已删除模块目录：/path/to/gtoolkits/functions/experimental_feature
# ✅ 已删除配置目录：/path/to/gtoolkits/configs/experimental_feature
#
# 🎉 模块 'experimental_feature' 删除成功！
```

## 配置示例

```json
{
  "_positional_args": {
    "module_name": "old_processor"
  },
  "force": false,
  "backup": false
}
```

## 注意事项

- **不可逆操作**：删除后无法自动恢复（除非有备份）
- **系统保护**：尝试删除保留模块会报错并阻止
- **确认提示**：默认需要输入 `y` 确认，可用 `--force` 跳过
- **部分存在**：如果只有模块目录或配置目录之一存在，也会删除存在的那个

## 相关文件

- 主模块：`functions/remove/main.py`
- 配置文件：`configs/remove/default.json`
