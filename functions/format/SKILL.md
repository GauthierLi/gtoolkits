---
name: format
description: "Format - 在此简要描述模块功能和触发场景。例如：用于 XXX 数据处理、YYY 分析等。使用当需要...时。"
homepage: ""
metadata: { "openclaw": { "emoji": "🔧", "requires": { "bins": [] } } }
---

# Format 模块

## 使用时机

✅ **使用场景：**
- 用户需要 XXX 功能时
- 需要处理 YYY 类型的数据时
- 执行 ZZZ 操作时

❌ **不使用场景：**
- 历史数据查询（应使用专门的归档工具）
- 实时数据流处理（应使用流式处理工具）
- 其他不适用情况

## 功能说明

### 主要功能

简要描述模块的核心功能...

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--input-param` | string | 否 | 输入参数说明 |
| `--debug` | bool | 否 | 调试模式 |

### 输出

描述模块的输出内容...

## 命令/用法

### 基本用法

```bash
# 使用默认配置运行
gtools format

# 使用启动脚本
gtools format start

# 指定参数运行
gtools format --input-param value --debug
```

### 配置文件方式

```bash
# 使用默认配置
gtools run --module-config configs/format/default.json

# 覆盖配置参数
gtools run --module-config configs/format/default.json --option debug=true
```

### 管道方式

```bash
# 在管道配置中使用
gtools run --config configs/pipeline.json
```

## 配置示例

```json
{
  "_positional_args": {
    "files": ["file1.txt", "file2.txt"]
  },
  "input_param": "value",
  "debug": true
}
```

## 注意事项

- 无 API key 需求
- 速率限制说明（如有）
- 其他需要注意的事项

## 相关文件

- 主模块：`functions/format/main.py`
- 配置文件：`configs/format/default.json`
- 启动脚本：`functions/format/start.sh`
