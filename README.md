# GTool Registry

基于注册机制的功能调用和配置系统，支持模块化开发、统一管理和可视化流程构建。

## 🌟 特性

- **装饰器注册**: 使用装饰器轻松注册功能函数和参数解析器
- **智能配置**: 支持 JSON 配置文件与命令行参数的智能合并
- **模块化架构**: 每个功能作为独立模块，便于管理和扩展
- **启动脚本支持**: 支持在模块中添加 start.sh 脚本进行自定义启动
- **自动发现**: 自动扫描和加载 `functions/` 目录下的模块
- **模块生命周期**: 内置 `create` 和 `remove` 命令管理模块
- **位置参数支持**: 配置文件支持 `_positional_args` 字段处理位置参数
- **命令行友好**: 完整的 CLI 界面和帮助系统
- **模块管道支持**: 通过配置文件定义模块执行顺序和参数，实现自动化管道执行
- **可视化界面**: 基于 Streamlit 的图形化节点构建器，支持拖拽式流程设计
- **依赖关系管理**: 可视化配置模块间的依赖关系，支持拓扑排序执行
- **实时执行监控**: 内置执行终端，支持实时查看全局日志和各节点日志
- **交互式参数配置**: 弹窗式参数配置界面，支持复杂参数类型的设置

## 🚀 快速开始

### 1. 安装

```bash
cd gtool_rv/
bash ./install.sh
```

### 2. 基本使用

#### 命令行界面

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

# 运行模块管道（按配置文件顺序执行多个模块）
gtools run --config system_config/config.json

# 查看模块帮助
gtools calculator -h
```

#### 可视化界面

```bash
# 启动可视化流程构建器
streamlit run app.py

# 或使用 Python 模块方式
python -m streamlit run app.py
```

可视化界面特性：
- 🖥️ **图形化节点构建**: 拖拽式添加和连接功能模块
- 🔗 **依赖关系配置**: 可视化设置模块间的依赖关系
- ⚙️ **交互式参数配置**: 弹窗界面配置复杂参数
- 📊 **实时执行监控**: 执行终端实时显示运行状态和日志
- 📋 **多节点日志查看**: 支持查看全局日志和各节点独立日志

## 📁 项目架构

```
gtool_registry_version/
├── app.py                     # Streamlit 可视化界面
├── gtools/                    # 主包（简化架构）
│   ├── __init__.py           # 包初始化
│   ├── __main__.py           # 命令行入口点
│   ├── registry.py           # 统一注册机制文件
│   └── cli.py                # 命令行接口实现
├── system_config/             # 模块管道配置文件目录
│   └── config.json           # 管道配置文件
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

## � 模块管道执行

系统支持通过配置文件定义模块执行管道，实现多个模块的顺序或依赖执行。

### 管道配置文件

创建 `system_config/config.json` 文件：

```json
{
  "working_directory": "/path/to/working/directory",
  "modules": [
    {
      "name": "calculator",
      "params": {
        "_positional_args": {
          "numbers": [1, 2, 3]
        },
        "operation": "add",
        "show_details": true
      }
    },
    {
      "name": "format",
      "params": {},
      "depends_on": ["calculator"]
    }
  ]
}
```

### 执行管道

```bash
# 运行模块管道
gtools run --config system_config/config.json
```

执行流程：
1. 读取配置文件并验证
2. 切换到指定工作目录
3. 按顺序执行每个模块
4. 每个模块使用配置的参数运行
5. 输出执行结果和日志

### 管道配置说明

- **working_directory**: 所有模块将在此目录下执行
- **modules**: 模块列表，按数组顺序执行
  - **name**: 模块名（必须在 `functions/` 下注册）
  - **params**: 模块参数，支持 `_positional_args` 和其他参数
  - **depends_on**: 可选，依赖的其他模块名列表，用于构建计算图（DAG）。如果指定，将按拓扑排序执行；否则按配置顺序执行

## 🎨 可视化流程构建器

系统提供基于 Streamlit 的可视化界面，支持图形化构建和执行模块流程。

### 启动可视化界面

```bash
streamlit run app.py
```

### 界面功能

#### 侧边栏配置
- **配置管理**: 加载或创建管道配置文件
- **节点添加**: 从已注册模块中选择并添加节点
- **参数配置**: 弹窗式参数配置界面，支持：
  - 字符串、整数、浮点数输入
  - 布尔值开关
  - 多选和单选列表
  - 位置参数配置
  - 依赖关系设置

#### 图形显示
- **计算顺序模式**: 显示节点执行顺序的箭头连接
- **依赖关系模式**: 显示节点间的依赖关系箭头
- **节点信息**: 显示节点名称、执行顺序和依赖状态

#### 执行终端
- **实时日志**: 执行过程中实时显示运行状态
- **多节点日志**: 支持查看全局日志和各节点独立日志
- **日志切换**: 执行前后可切换查看不同节点的日志

### 使用流程

1. **加载配置**: 从侧边栏加载或创建配置文件
2. **添加节点**: 选择功能模块并配置参数
3. **设置依赖**: 为节点配置依赖关系（可选）
4. **查看图形**: 在主界面查看节点关系图
5. **执行流程**: 点击"Execute Graph"运行整个流程
6. **查看日志**: 在执行终端查看实时运行日志

### 优势特点

- **直观易用**: 无需编写配置文件，直接拖拽构建流程
- **实时反馈**: 执行过程实时显示，日志即时更新
- **灵活配置**: 支持复杂参数类型和依赖关系
- **即见即所得**: 图形化展示执行顺序和依赖关系

## �🗑️ 模块管理

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

### 可视化界面示例

1. **启动界面**:
   ```bash
   streamlit run app.py
   ```

2. **构建简单流程**:
   - 加载配置文件
   - 添加 Calculator 节点，配置参数：数字 10, 20, 操作 multiply
   - 添加 Test Module 节点，设置为依赖 Calculator
   - 查看图形显示的依赖关系
   - 点击执行，观察实时日志输出

3. **复杂管道构建**:
   - 创建多个节点
   - 配置复杂的依赖关系
   - 使用拓扑排序查看执行顺序
   - 实时监控各节点执行状态

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
- **可视化流程设计**: 图形化构建复杂的数据处理管道
- **依赖管理**: 可视化管理模块间的复杂依赖关系
- **实时监控**: 执行过程的实时状态监控和日志查看

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