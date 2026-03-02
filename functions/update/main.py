"""
Update 模块：自动解析 parse_args 函数并生成/更新配置文件
用法：gtools update <module_name>
"""

import argparse
import ast
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from gtools.registry import ARGS, FUNCTION


@FUNCTION.regist(module_name="update")
def main(args: argparse.Namespace):
    """主函数：更新模块的配置文件"""
    module_name = args.module_name

    # 检查模块是否存在
    base_dir = Path(__file__).parent.parent.parent
    module_dir = base_dir / "functions" / module_name

    if not module_dir.exists():
        print(f"❌ 模块 '{module_name}' 不存在！")
        print(f"路径：{module_dir}")
        return

    module_file = module_dir / "main.py"
    if not module_file.exists():
        print(f"❌ 模块文件不存在：{module_file}")
        return

    print(f"🔄 开始更新模块 '{module_name}' 的配置...")

    try:
        # 解析模块文件中的 parse_args 函数
        config_data = parse_module_args(module_file, module_name)

        if not config_data:
            print(f"❌ 无法在模块 '{module_name}' 中找到有效的参数定义")
            return

        # 创建或更新配置文件
        config_dir = base_dir / "configs" / module_name
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "default.json"

        # 如果配置文件已存在且不强制覆盖，进行合并
        existing_config = {}
        if config_file.exists() and not args.force:
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
                print(f"📄 发现已存在的配置文件，将进行智能合并...")
            except Exception as e:
                print(f"⚠️  读取现有配置失败：{e}")

        # 合并配置
        final_config = merge_configs(existing_config, config_data)

        # 写入配置文件
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(final_config, f, ensure_ascii=False, indent=2)

        print(f"✅ 配置文件已更新：{config_file}")

        # 显示更新信息
        show_config_summary(final_config, module_name, args.verbose)

        # 如果指定了 --skill 或模块中没有 SKILL.md，创建技能模板
        if args.skill or args.auto_skill:
            create_skill_template(module_dir, module_name, base_dir, args.verbose)

    except Exception as e:
        print(f"❌ 更新配置时发生错误：{e}")
        if args.verbose:
            import traceback

            traceback.print_exc()


def create_skill_template(module_dir: Path, module_name: str, base_dir: Path, verbose: bool = False):
    """创建或补充 SKILL.md 模板"""
    skill_file = module_dir / "SKILL.md"
    
    if skill_file.exists():
        print(f"ℹ️  SKILL.md 已存在，跳过创建")
        return
    
    print(f"📦 检测到模块缺少 SKILL.md，正在创建技能模板...")
    
    try:
        # 获取 create 模块的模板路径
        create_template_dir = base_dir / "functions" / "create" / "reference"
        template_skill = create_template_dir / "SKILL.md"
        
        if not template_skill.exists():
            print(f"⚠️  警告：SKILL.md 模板文件不存在：{template_skill}")
            return
        
        with open(template_skill, "r", encoding="utf-8") as f:
            skill_content = f.read()

        # 替换占位符
        skill_content = replace_placeholders(skill_content, module_name)

        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(skill_content)
        
        print(f"✅ 创建技能包模板：{skill_file}")
        
        if verbose:
            print(f"\n🐱 技能包后续步骤:")
            print(f"   1. 编辑 {skill_file} 完善技能描述")
            print(f"   2. 参考 OpenClaw 技能包格式 (name, description 必填)")
            print(f"   3. 可添加 scripts/, references/, assets/ 目录")
            print(f"   4. 使用 OpenClaw 技能打包工具打包")
    
    except Exception as e:
        print(f"⚠️  创建 SKILL.md 失败：{e}")


def replace_placeholders(content: str, module_name: str) -> str:
    """替换模板文件中的占位符"""
    # 生成不同格式的模块名
    module_name_title = module_name.replace("_", " ").title().replace(" ", "_")

    replacements = {
        "{MODULE_NAME}": module_name,
        "{MODULE_NAME_TITLE}": module_name_title,
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


def parse_module_args(module_file: Path, module_name: str) -> Optional[Dict[str, Any]]:
    """解析模块文件中的 parse_args 函数，提取参数定义"""
    try:
        with open(module_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 AST
        tree = ast.parse(content)

        # 查找 parse_args 函数
        parse_args_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "parse_args":
                parse_args_func = node
                break

        if not parse_args_func:
            print(f"⚠️  未找到 parse_args 函数")
            return None

        # 解析参数定义
        config_data = extract_arguments_from_ast(parse_args_func)
        return config_data

    except Exception as e:
        print(f"❌ 解析模块文件失败：{e}")
        return None


def extract_arguments_from_ast(func_node: ast.FunctionDef) -> Dict[str, Any]:
    """从 AST 节点中提取参数定义"""
    config = {}
    positional_args = {}

    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # 查找 parser.add_argument 调用
            if node.func.attr == "add_argument":
                arg_info = extract_argument_info(node)
                if arg_info:
                    arg_name, arg_config, is_positional = arg_info
                    if is_positional:
                        positional_args[arg_name] = arg_config
                    else:
                        config[arg_name] = arg_config

    # 如果有位置参数，添加到配置中
    if positional_args:
        config["_positional_args"] = positional_args

    return config


def extract_argument_info(call_node: ast.Call) -> Optional[tuple]:
    """从 add_argument 调用中提取参数信息"""
    try:
        # 获取参数名
        if not call_node.args:
            return None

        first_arg = call_node.args[0]
        if isinstance(first_arg, ast.Constant):
            arg_name = first_arg.value
        elif isinstance(first_arg, ast.Str):  # Python < 3.8 兼容性
            arg_name = first_arg.s
        else:
            return None

        # 判断是否为位置参数（不以 - 开头）
        is_positional = not arg_name.startswith("-")

        # 如果是可选参数，提取 dest 名称
        if not is_positional:
            dest_name = arg_name.lstrip("-").replace("-", "_")
        else:
            dest_name = arg_name

        # 提取默认值
        default_value = None
        arg_type = None

        for keyword in call_node.keywords:
            if keyword.arg == "default":
                default_value = extract_value(keyword.value)
            elif keyword.arg == "type":
                # 尝试推断类型
                if isinstance(keyword.value, ast.Name):
                    if keyword.value.id == "str":
                        arg_type = str
                    elif keyword.value.id == "int":
                        arg_type = int
                    elif keyword.value.id == "float":
                        arg_type = float
                    elif keyword.value.id == "bool":
                        arg_type = bool
            elif keyword.arg == "action":
                action_value = extract_value(keyword.value)
                if action_value == "store_true":
                    default_value = False
                    arg_type = bool
                elif action_value == "store_false":
                    default_value = True
                    arg_type = bool
            elif keyword.arg == "nargs":
                nargs_value = extract_value(keyword.value)
                if nargs_value in ["*", "+"]:
                    # 列表类型参数
                    if default_value is None:
                        default_value = []

        # 如果没有明确的默认值，根据类型设置
        if default_value is None:
            if arg_type == str:
                default_value = ""
            elif arg_type == int:
                default_value = 0
            elif arg_type == float:
                default_value = 0.0
            elif arg_type == bool:
                default_value = False
            else:
                default_value = None

        return dest_name, default_value, is_positional

    except Exception as e:
        print(f"⚠️  提取参数信息失败：{e}")
        return None


def extract_value(node: ast.AST) -> Any:
    """从 AST 节点中提取值"""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):  # Python < 3.8
        return node.s
    elif isinstance(node, ast.Num):  # Python < 3.8
        return node.n
    elif isinstance(node, ast.NameConstant):  # Python < 3.8
        return node.value
    elif isinstance(node, ast.List):
        return [extract_value(item) for item in node.elts]
    elif isinstance(node, ast.Dict):
        return {
            extract_value(k): extract_value(v) for k, v in zip(node.keys, node.values)
        }
    else:
        return None


def merge_configs(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """智能合并现有配置和新配置"""
    result = existing.copy()

    for key, value in new.items():
        if key not in result:
            # 新参数，直接添加
            result[key] = value
        else:
            # 已存在的参数，保留现有值但更新类型一致性
            existing_value = result[key]
            if type(existing_value) != type(value) and value is not None:
                # 类型不匹配，提示用户
                print(
                    f"⚠️  参数 '{key}' 类型发生变化：{type(existing_value).__name__} -> {type(value).__name__}"
                )

    return result


def show_config_summary(
    config: Dict[str, Any], module_name: str, verbose: bool = False
):
    """显示配置摘要"""
    print(f"\n📊 配置摘要:")
    print("=" * 50)

    if "_positional_args" in config:
        pos_args = config["_positional_args"]
        print(f"📍 位置参数：{len(pos_args)} 个")
        if verbose:
            for name, value in pos_args.items():
                print(f"  • {name}: {value}")

    optional_args = {k: v for k, v in config.items() if k != "_positional_args"}
    print(f"⚙️  可选参数：{len(optional_args)} 个")
    if verbose:
        for name, value in optional_args.items():
            print(f"  • {name}: {value} ({type(value).__name__})")

    print(f"\n💡 提示：使用 gtools {module_name} 测试配置")


@ARGS.regist(module_name="update")
def parse_args():
    """参数解析函数：定义 update 模块接受的参数"""
    parser = argparse.ArgumentParser(
        description="Update 模块 - 自动解析模块参数并生成配置文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  gtools update my_module                # 更新模块配置
  gtools update my_module --force        # 强制覆盖现有配置
  gtools update my_module --verbose      # 显示详细信息
  gtools update my_module --skill        # 同时创建 SKILL.md 模板（如果不存在）
  gtools update my_module --auto-skill   # 自动检测并创建 SKILL.md（如果不存在）
        """.strip(),
    )

    parser.add_argument("module_name", help="要更新配置的模块名称")

    parser.add_argument(
        "--force", "-f", action="store_true", help="强制覆盖现有配置文件"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")

    parser.add_argument(
        "--skill", "-s", action="store_true", help="创建 SKILL.md 模板（如果不存在）"
    )

    parser.add_argument(
        "--auto-skill",
        action="store_true",
        help="自动检测并创建 SKILL.md 模板（如果不存在）",
    )

    return parser
