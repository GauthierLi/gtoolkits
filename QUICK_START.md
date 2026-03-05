# GTool Registry 快速开始指南

本指南将通过创建一个简单的 `hello_world` 模块，带您快速了解 GTool Registry 的核心功能。

## 📋 前置要求

确保您已经安装了 GTool Registry：

```bash
cd gtool_registry_version/
bash ./install.sh
```
## 🚀 快速开始

### 步骤 1: 创建新模块

使用内置命令创建 `hello_world` 模块：

```bash
gtools create hello_world
```

**预期输出：**
```
运行模块: create
🚀 开始创建新模块: hello_world
✅ 创建目录: /Users/liweikang/Code/gtool_registry_version/functions/hello_world
✅ 创建文件: /Users/liweikang/Code/gtool_registry_version/functions/hello_world/main.py
✅ 创建配置文件: /Users/liweikang/Code/gtool_registry_version/configs/hello_world/default.json
✅ 创建启动脚本: /Users/liweikang/Code/gtool_registry_version/functions/hello_world/start.sh

🎉 模块 'hello_world' 创建成功！
📂 模块路径: /Users/liweikang/Code/gtool_registry_version/functions/hello_world
⚙️  配置路径: /Users/liweikang/Code/gtool_registry_version/configs/hello_world

📖 使用方法:
   gtools hello_world           # 使用默认配置运行
   gtools hello_world start     # 执行启动脚本
   gtools hello_world --help   # 查看帮助信息

📝 配置文件说明:
   • 位置参数配置: 使用 "_positional_args" 字段
     例如: "_positional_args": {"files": ["file1.txt", "file2.txt"]}
   • 可选参数配置: 直接在顶层配置
     例如: "debug": true, "items": ["a", "b"]
   • 布尔参数: true/false
   • 列表参数: ["item1", "item2"]
```

### 步骤 1.5: 修改模块代码

创建模块后，您可以根据需要修改生成的代码文件。让我们修改 `hello_world` 模块，使其具有更有趣的功能。

#### 修改 main.py 文件

打开 `functions/hello_world/main.py` 文件，将内容替换为：

```python
"""
Hello World 模块：简单的问候模块示例
"""

import argparse

from gtools.registry import ARGS, FUNCTION


@FUNCTION.regist(module_name="hello_world")
def main(args: argparse.Namespace):
    """主函数：hello_world 模块的主要逻辑"""
    print("🔧 hello_world 模块执行中...")

    if args.verbose:
        print("📝 详细模式已启用")
        print("🎯 参数配置:")
        print(f"   - 名字: {args.name}")
        print(f"   - 问候语: {args.greeting}")
        print(f"   - 详细模式: {args.verbose}")

    print(f"{args.greeting}, {args.name}!")
    print("✅ 执行完成！")


@ARGS.regist(module_name="hello_world")
def parse_args():
    """参数解析函数：定义 hello_world 模块接受的参数"""
    parser = argparse.ArgumentParser(
        description="Hello World - 示例模块",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  gtools hello_world                          # 使用默认配置
  gtools hello_world --name "Alice"          # 指定名字
  gtools hello_world --greeting "Hi"         # 指定问候语
  gtools hello_world --verbose               # 启用详细输出
        """.strip(),
    )

    parser.add_argument(
        "--name",
        type=str,
        default="World",
        help="要问候的名字 (默认: World)",
    )

    parser.add_argument(
        "--greeting",
        type=str,
        default="Hello",
        help="问候语 (默认: Hello)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="启用详细输出 (默认: False)",
    )

    return parser
```

#### 修改 start.sh 文件

打开 `functions/hello_world/start.sh` 文件，将内容替换为：

```bash
#!/bin/bash

# Hello World 模块启动脚本

echo "🔧 hello_world 模块启动脚本执行中..."
echo "Hello from start.sh script!"

# 显示参数信息
echo "参数数量: $#"
if [ $# -gt 0 ]; then
    echo "参数列表: $@"
fi

echo "✅ 启动脚本执行完成！"
```

**提示：** 修改代码后，无需重新注册模块，GTool Registry 会自动重新加载代码。

### 步骤 2: 查看模块信息

查看刚创建的模块信息：

```bash
gtools info hello_world
```

**预期输出：**
```
模块信息: hello_world
--------------------------------------------------
╔══════════════════╤════════╗
║ 属性             │  状态  ║
╟──────────────────┼────────╢
║ 函数已注册       │  ✓ 是  ║
╟──────────────────┼────────╢
║ 参数解析器已注册 │  ✓ 是  ║
╟──────────────────┼────────╢
║ 包含 start.sh    │  ✓ 是  ║
╟──────────────────┼────────╢
║ 模块完整性       │ ✓ 完整 ║
╟──────────────────┼────────╢
║ 配置文件存在     │  ✓ 是  ║
╚══════════════════╧════════╝

配置文件路径: /Users/liweikang/Code/gtool_registry_version/configs/hello_world/default.json
start.sh 路径: /Users/liweikang/Code/gtool_registry_version/functions/hello_world/start.sh
使用命令: gtools hello_world start
```

### 步骤 3: 查看所有模块

确认新模块已注册：

```bash
gtools list
```

**预期输出：**
```
已注册的模块:
----------------------------------------------------------------------
╔══════════════════╤══════════╤══════════╗
║ 模块名            │  注册状态 │ start.sh ║
╟──────────────────┼──────────┼──────────╢
║ calculator       │  ✓ 完整  │   ✓ 有   ║
╟──────────────────┼──────────┼──────────╢
║ create           │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ format           │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ hello_world      │  ✓ 完整  │   ✓ 有   ║
╟──────────────────┼──────────┼──────────╢
║ mark_imgs        │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ remove           │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ test_module      │  ✓ 完整  │   ✓ 有   ║
╟──────────────────┼──────────┼──────────╢
║ update           │  ✓ 完整  │   ✗ 无   ║
╚══════════════════╧══════════╧══════════╝

总计: 9 个模块
说明:
  • 注册状态: ✓ 表示模块完整注册（有函数和参数解析器），✗ 表示注册不完整
  • start.sh: ✓ 表示模块包含启动脚本，✗ 表示无启动脚本
  • 使用 'gtools <module_name> start' 执行包含启动脚本的模块
```

### 步骤 4: 运行模块

使用默认配置运行模块：

```bash
gtools hello_world
```

**预期输出：**
```
运行模块: hello_world
🔧 hello_world 模块执行中...
Hello, World!
✅ 执行完成！
```

### 步骤 5: 查看模块帮助

查看模块的帮助信息：

```bash
gtools hello_world --help
```

**预期输出：**
```
usage: gtools [-h] [--name NAME] [--greeting GREETING] [--verbose]

Hello World - 示例模块

options:
  -h, --help           show this help message and exit
  --name NAME          要问候的名字 (默认: World)
  --greeting GREETING  问候语 (默认: Hello)
  --verbose            启用详细输出 (默认: False)

使用示例:
  gtools hello_world                          # 使用默认配置
  gtools hello_world --name "Alice"          # 指定名字
  gtools hello_world --greeting "Hi"         # 指定问候语
  gtools hello_world --verbose               # 启用详细输出
```

### 步骤 6: 使用自定义参数运行

使用自定义参数运行模块：

```bash
gtools hello_world --name "Alice" --greeting "Hi" --verbose
```

**预期输出：**
```
运行模块: hello_world
🔧 hello_world 模块执行中...
📝 详细模式已启用
🎯 参数配置:
   - 名字: Alice
   - 问候语: Hi
   - 详细模式: True
Hi, Alice!
✅ 执行完成！
```

### 步骤 7: 执行启动脚本

执行模块的启动脚本：

```bash
gtools hello_world start
```

**预期输出：**
```
 hello_world 模块启动脚本执行中...
Hello from start.sh script!
参数数量: 0
✅ 启动脚本执行完成！
```

### 步骤 8: 使用启动脚本传递参数

向启动脚本传递参数：

```bash
gtools hello_world start arg1 arg2 arg3
```

**预期输出：**
```
 hello_world 模块启动脚本执行中...
Hello from start.sh script!
参数数量: 3
参数列表: arg1 arg2 arg3
✅ 启动脚本执行完成！
```

## 🧹 清理

### 删除创建的模块

删除 `hello_world` 模块以保持项目干净：

```bash
gtools remove hello_world --force
```

**预期输出：**
```
运行模块: remove
🗑️  准备删除模块: hello_world
� 模块目录: /Users/liweikang/Code/gtool_registry_version/functions/hello_world
⚙️  配置目录: /Users/liweikang/Code/gtool_registry_version/configs/hello_world
✅ 已删除模块目录: /Users/liweikang/Code/gtool_registry_version/functions/hello_world
✅ 已删除配置目录: /Users/liweikang/Code/gtool_registry_version/configs/hello_world

🎉 模块 'hello_world' 删除成功！
已删除 2 个项目:
  • 模块目录: /Users/liweikang/Code/gtool_registry_version/functions/hello_world
  • 配置目录: /Users/liweikang/Code/gtool_registry_version/configs/hello_world
```

### 验证删除

确认模块已被删除：

```bash
gtools list
```

**预期输出：**
```
已注册的模块:
----------------------------------------------------------------------
╔══════════════════╤══════════╤══════════╗
║ 模块名            │  注册状态 │ start.sh ║
╟──────────────────┼──────────┼──────────╢
║ calculator       │  ✓ 完整  │   ✓ 有   ║
╟──────────────────┼──────────┼──────────╢
║ create           │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ format           │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ mark_imgs        │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ remove           │  ✓ 完整  │   ✗ 无   ║
╟──────────────────┼──────────┼──────────╢
║ test_module      │  ✓ 完整  │   ✓ 有   ║
╟──────────────────┼──────────┼──────────╢
║ update           │  ✓ 完整  │   ✗ 无   ║
╚══════════════════╧══════════╧══════════╝

总计: 8 个模块
说明:
  • 注册状态: ✓ 表示模块完整注册（有函数和参数解析器），✗ 表示注册不完整
  • start.sh: ✓ 表示模块包含启动脚本，✗ 表示无启动脚本
  • 使用 'gtools <module_name> start' 执行包含启动脚本的模块
```

## � 可视化界面

GTool Registry 提供了基于 Streamlit 的可视化界面，支持图形化构建和执行模块流程。

### 启动可视化界面

```bash
# 方法1: 直接运行
streamlit run app.py

# 方法2: 使用 Python 模块方式
python -m streamlit run app.py
```

### 界面使用流程

1. **加载配置**: 从侧边栏加载或创建管道配置文件
2. **添加节点**: 选择功能模块并配置参数
3. **设置依赖**: 为节点配置依赖关系（可选）
4. **查看图形**: 在主界面查看节点关系图
5. **执行流程**: 点击"Execute Graph"运行整个流程
6. **查看日志**: 在执行终端查看实时运行日志

