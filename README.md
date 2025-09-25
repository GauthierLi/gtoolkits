# gtool_registry_version

基于注册机制的功能调用和配置系统

## 🌟 特性

- **简单易用**: 使用装饰器轻松注册功能函数和参数解析器
- **配置管理**: 支持默认配置文件和命令行参数覆盖
- **模块化设计**: 每个功能作为独立模块，便于管理和扩展  
- **自动发现**: 自动扫描和加载已注册的模块
- **命令行友好**: 提供完整的命令行界面和帮助系统

## 🚀 快速开始

### 1. 安装

```bash
cd gtool_registry_version/
bash ./install.sh
```

### 2. 使用示例

#### 注册功能模块

```python
from gtools.registry import FUNCTION, ARGS
import argparse

@FUNCTION.regist(module_name='my_module')
def main(args: argparse.Namespace):
    print(f"Hello from {args.name}!")
    print(f"配置文件: {args.config_file}")

@ARGS.regist(module_name='my_module')
def parse_args():
    parser = argparse.ArgumentParser("my_module")
    parser.add_argument("--config-file", "-c", type=str, default="config.json")
    parser.add_argument("--name", type=str, default="World")
    return parser
```

#### 命令行使用

```bash
# 列出所有已注册模块
gtools list

# 查看模块信息
gtools info my_module

# 运行模块（使用默认配置）
gtools my_module

# 运行模块并覆盖参数
gtools my_module --name "Alice" --config-file custom.json

# 查看模块帮助
gtools my_module -h
```

## 📁 项目结构

```
gtool_registry_version/
├── gtools/                 # 主包
│   ├── __init__.py        # 包初始化
│   ├── __main__.py        # 命令行入口
│   ├── registry.py        # 注册机制入口
│   ├── cli.py            # 命令行界面
│   └── common/           # 通用工具和类
│       ├── __init__.py   # 通用模块初始化
│       ├── registry.py   # 注册器实现
│       ├── config.py     # 配置处理
│       └── utils.py      # 工具函数
├── functions/             # 功能模块目录
│   ├── __init__.py
│   ├── test_module/      # 测试功能模块
│   │   ├── __init__.py
│   │   └── main.py       # 模块主文件
│   └── calculator/       # 计算器功能模块
│       ├── __init__.py
│       └── main.py       # 模块主文件
├── configs/               # 配置文件目录
│   ├── test_module/
│   │   └── default.json   # 默认配置
│   └── calculator/
│       └── default.json
├── tests/                 # 测试文件
│   └── test_gtools.py
├── install.sh            # 安装脚本
├── setup.py              # 打包配置
├── README.md             # 项目说明
└── FUNCTION.md           # 功能说明
```

## 🔧 核心概念

### 注册机制

使用两个装饰器来注册功能：

- `@FUNCTION.regist(module_name='xxx')`: 注册主函数
- `@ARGS.regist(module_name='xxx')`: 注册参数解析器

### 配置文件系统

- 默认配置文件位置: `configs/{module_name}/default.json`
- 命令行参数会自动覆盖配置文件中的相同字段
- 支持嵌套配置和复杂数据类型

### 模块发现

系统会自动扫描 `functions/` 目录下的子目录，并导入其中的 `main.py` 文件来加载注册函数。

## 🏗️ 添加新功能模块

要添加新的功能模块，只需：

1. 在 `functions/` 目录下创建一个新的子目录
2. 在子目录中创建 `main.py` 文件
3. 在 `main.py` 中使用装饰器注册功能：

```python
# functions/my_new_function/main.py
from gtools.registry import FUNCTION, ARGS
import argparse

@FUNCTION.regist(module_name='my_new_function')
def main(args):
    print(f"Hello from {args.name}")

@ARGS.regist(module_name='my_new_function')
def parse_args():
    parser = argparse.ArgumentParser("my_new_function")
    parser.add_argument("--name", default="World")
    return parser
```

4. （可选）在 `configs/my_new_function/default.json` 中添加默认配置

## 📝 配置文件示例

`configs/test_module/default.json`:
```json
{
  "config_file": "configs/test_module/default.json",
  "output_dir": "/tmp/gtools_test_output",
  "verbose": false,
  "dry_run": false,
  "items": ["item1", "item2", "item3"]
}
```

## 🎯 使用场景

- **工具集管理**: 统一管理多个独立的工具脚本
- **批处理系统**: 配置化的批处理任务执行
- **插件系统**: 动态加载和执行功能模块
- **配置管理**: 复杂参数的配置文件管理

## 🧪 测试

运行测试脚本：

```bash
python tests/test_gtools.py
```

测试包含的功能：
- 注册机制验证
- 命令行接口测试
- 配置文件处理测试

## 🌈 示例模块

项目包含两个示例模块：

### test_module
演示基本的注册和配置功能：
```bash
gtools test_module                    # 使用默认配置
gtools test_module -v --dry-run      # 启用详细模式和试运行
gtools test_module --items a b c     # 指定处理项目
```

### calculator
简单计算器功能：
```bash
gtools calculator 1 2 3 4 5                      # 默认求和
gtools calculator 2 3 4 --operation multiply     # 乘法运算  
gtools calculator 10 20 30 --operation average   # 求平均值
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者的支持！