# GTool Registry

基于注册机制的功能调用和配置系统，支持模块化开发和统一管理。

## 🌟 特性

- **装饰器注册**: 使用装饰器轻松注册功能函数和参数解析器
- **智能配置**: 支持 JSON 配置文件与命令行参数的智能合并
- **模块化架构**: 每个功能作为独立模块，便于管理和扩展
- **启动脚本支持**: 支持在模块中添加 start.sh 脚本进行自定义启动
- **自动发现**: 自动扫描和加载 `functions/` 目录下的模块
- **模块生命周期**: 内置 `create` 和 `remove` 命令管理模块
- **位置参数支持**: 配置文件支持 `_positional_args` 字段处理位置参数
- **命令行友好**: 完整的 CLI 界面和帮助系统

## 🚀 快速开始

### 1. 安装

```bash
cd gtool_registry_version/
bash ./install.sh
```

### 2. 基本使用

```bash
# 列出所有已注册模块
gtools list

# 查看模块详细信息
gtools info calculator

# 运行模块（使用默认配置）
gtools calculator

# 覆盖参数运行模块
gtools calculator 10 20 --operation multiply

# 执行模块的启动脚本（如果存在 start.sh）
gtools calculator start

# 执行模块的启动脚本并传递参数
gtools calculator start 100 200 300

# 查看模块帮助
gtools calculator -h
```

## 📁 项目架构

```
gtool_registry_version/
├── gtools/                    # 主包（简化架构）
│   ├── __init__.py           # 包初始化
│   ├── __main__.py           # 命令行入口点
│   ├── registry.py           # 统一注册机制文件
│   └── cli.py                # 命令行接口实现
├── functions/                 # 功能模块目录
│   ├── calculator/           # 计算器模块
│   │   ├── main.py          # 模块主文件
│   │   └── start.sh         # 启动脚本（可选）
│   ├── test_module/          # 测试模块
│   │   ├── main.py          # 模块主文件
│   │   └── start.sh         # 启动脚本（可选）
│   ├── create/               # 模块创建工具
│   │   ├── main.py
│   │   └── reference/        # 模板文件
│   │       ├── main.py       # Python 模块模板
│   │       └── default.json  # 配置文件模板
│   └── remove/               # 模块删除工具
│       └── main.py
├── configs/                   # 配置文件目录
│   ├── calculator/
│   │   └── default.json
│   ├── test_module/
│   │   └── default.json
│   └── ...
├── tests/
│   └── test_gtools.py
├── install.sh
├── setup.py
└── README.md
```

## 🔧 创建新模块

### 自动创建（推荐）

```bash
# 使用内置命令创建新模块
gtools create my_awesome_tool

# 查看创建的模块
gtools list

# 运行新创建的模块
gtools my_awesome_tool --help
gtools my_awesome_tool --debug

# 执行自动生成的启动脚本
gtools my_awesome_tool start
```

创建模块时会自动生成：
- `main.py` - 模块主文件
- `default.json` - 配置文件  
- `start.sh` - 启动脚本模板（包含参数处理示例）

### 手动创建

如果你喜欢手动创建，可以参考以下结构：

```python
# functions/my_module/main.py
from gtools.registry import FUNCTION, ARGS
import argparse

@FUNCTION.regist(module_name='my_module')
def main(args: argparse.Namespace):
    print(f"🔧 my_module 模块执行中...")
    print(f"参数: {args}")
    print("✅ 执行完成！")

@ARGS.regist(module_name='my_module')
def parse_args():
    parser = argparse.ArgumentParser(
        description="My Module - 模块描述"
    )
    parser.add_argument("--input-param", type=str, default="default_value")
    parser.add_argument("--debug", action="store_true")
    return parser
```

## 🚀 启动脚本支持

模块可以包含可选的 `start.sh` 启动脚本，用于自定义启动逻辑。

```bash
# 执行模块的启动脚本
gtools my_module start

# 传递参数给启动脚本
gtools my_module start param1 param2
```

脚本会在模块目录中执行，接收传递的所有参数。你可以在脚本中定义任何你需要的逻辑。

## 📝 配置文件系统


### 基本配置

```json
{
  "input_param": "default_value",
  "debug": false
}
```

### 位置参数配置

```json
{
  "_positional_args": {
    "numbers": [1, 2, 3, 4, 5]
  },
  "operation": "add",
  "show_details": true
}
```

配置文件特性：
- 命令行参数会自动覆盖配置文件中的同名字段
- `_positional_args` 字段用于配置位置参数
- 支持复杂数据类型（数组、对象等）

## 🗑️ 模块管理

### 删除模块

```bash
# 列出可删除的模块
gtools remove --list

# 删除模块（需要确认）
gtools remove my_module

# 强制删除（跳过确认）
gtools remove my_module --force
```

### 模块保护

以下模块受保护，无法删除：
- `create` - 模块创建工具
- `remove` - 模块删除工具  
- `calculator` - 示例计算器
- `test_module` - 示例测试模块

## 🌈 内置示例

### Calculator 模块
```bash
# 使用默认配置（加法）
gtools calculator

# 指定数字和操作
gtools calculator 10 20 30 --operation multiply

# 查看详细信息
gtools calculator 5 10 15 --operation average --show-details

# 使用启动脚本执行
gtools calculator start

# 使用启动脚本并传递数字参数
gtools calculator start 100 200 300
```

### Test Module 模块
```bash
# 使用默认配置
gtools test_module

# 启用详细模式
gtools test_module --verbose --dry-run

# 指定处理项目
gtools test_module --items item1 item2 item3
```

## 🧪 测试

```bash
python tests/test_gtools.py
```

## 🎯 使用场景

- **工具集统一管理**: 将多个独立脚本统一管理
- **批处理任务**: 配置化的批处理任务执行
- **插件系统**: 动态加载和执行功能模块
- **配置驱动**: 复杂参数的配置文件管理
- **团队协作**: 标准化的模块开发和部署流程

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者的支持和反馈！