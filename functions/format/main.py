"""
Format 模块：使用代码格式化工具扫描和格式化 Python 文件
支持 pylint、black、isort 等多种工具
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from gtools.registry import ARGS, FUNCTION


def get_tool_path(tool_name: str) -> str:
    """获取工具的完整路径"""
    # 首先尝试直接调用
    try:
        result = subprocess.run(
            [tool_name, "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return tool_name
    except FileNotFoundError:
        pass

    # 如果在虚拟环境中，尝试使用完整路径
    venv_path = os.path.dirname(sys.executable)
    tool_path = os.path.join(venv_path, tool_name)

    try:
        result = subprocess.run(
            [tool_path, "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return tool_path
    except FileNotFoundError:
        pass

    return tool_name  # 回退到原始名称


def check_tool_available(tool_name: str) -> bool:
    """检查工具是否可用"""
    tool_path = get_tool_path(tool_name)
    try:
        result = subprocess.run(
            [tool_path, "--version"], capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def find_python_files(path: str, recursive: bool = True) -> List[str]:
    """查找 Python 文件"""
    python_files = []

    if os.path.isfile(path):
        if path.endswith(".py"):
            python_files.append(path)
    else:
        if recursive:
            for root, dirs, files in os.walk(path):
                # 跳过 __pycache__ 目录
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for file in files:
                    if file.endswith(".py"):
                        python_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(path):
                if file.endswith(".py"):
                    python_files.append(os.path.join(path, file))

    return python_files


def check_available_tools() -> List[str]:
    """检查可用的格式化工具"""
    tools = []

    # 检查 pylint
    if check_tool_available("pylint"):
        tools.append("pylint")

    # 检查 black
    if check_tool_available("black"):
        tools.append("black")

    # 检查 isort
    if check_tool_available("isort"):
        tools.append("isort")

    # 检查 autopep8
    if check_tool_available("autopep8"):
        tools.append("autopep8")

    return tools


def run_pylint_check(
    file_path: str, min_score: float = 8.0, disable_checks=None, config_file=None
) -> bool:
    """运行 pylint 检查"""
    try:
        tool_path = get_tool_path("pylint")

        # 构建 pylint 命令
        cmd = [tool_path, file_path, "--score=yes"]

        # 添加禁用检查项
        if disable_checks:
            disable_str = ",".join(disable_checks)
            cmd.extend(["--disable", disable_str])

        # 添加配置文件
        if config_file and os.path.exists(config_file):
            cmd.extend(["--rcfile", config_file])

        result = subprocess.run(cmd, capture_output=True, text=True)

        # 提取评分
        lines = result.stdout.split("\n")
        score_line = [line for line in lines if "rated at" in line]

        if score_line:
            import re

            match = re.search(r"(\d+\.\d+)/10", score_line[0])
            if match:
                score = float(match.group(1))
                if score < min_score:
                    print(f"  ⚠️  Pylint 评分: {score}/10 (低于 {min_score})")

                    # 分析问题类型
                    format_issues = []
                    quality_issues = []
                    disabled_issues = []

                    for line in lines:
                        if any(
                            x in line
                            for x in ["C0103", "C0114", "C0115", "C0116", "W0613"]
                        ):  # 格式相关
                            format_issues.append(line.strip())
                        elif any(
                            x in line for x in ["W0611", "W1309", "R0903", "R0913"]
                        ):  # 质量相关
                            if disable_checks and any(
                                check in line for check in disable_checks
                            ):
                                disabled_issues.append(line.strip())
                            else:
                                quality_issues.append(line.strip())

                    if format_issues:
                        print(f"    💡 格式问题 (可自动修复): {len(format_issues)} 个")
                    if quality_issues:
                        print(f"    🔧 质量问题 (需手动修复): {len(quality_issues)} 个")
                        # 显示前3个质量问题
                        for issue in quality_issues[:3]:
                            if file_path in issue:
                                print(f"      • {issue}")
                    if disabled_issues:
                        print(f"    🔕 已忽略问题: {len(disabled_issues)} 个")

                    return True
                else:
                    print(f"  ✅ Pylint 评分: {score}/10")
                    if disable_checks:
                        print(
                            f"    🔕 已禁用检查: {', '.join(disable_checks[:3])}{'...' if len(disable_checks) > 3 else ''}"
                        )

        return False
    except Exception as e:
        print(f"  ❌ Pylint 检查失败: {e}")
        return False


def run_black_check(file_path: str) -> bool:
    """检查 black 格式化"""
    try:
        tool_path = get_tool_path("black")
        result = subprocess.run(
            [tool_path, "--check", file_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  ⚠️  需要 Black 格式化")
            return True
        else:
            print(f"  ✅ Black 格式符合标准")
            return False
    except Exception as e:
        print(f"  ❌ Black 检查失败: {e}")
        return False


def run_isort_check(file_path: str) -> bool:
    """检查 isort 导入排序"""
    try:
        tool_path = get_tool_path("isort")
        result = subprocess.run(
            [tool_path, "--check-only", file_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  ⚠️  需要导入排序")
            return True
        else:
            print(f"  ✅ 导入排序符合标准")
            return False
    except Exception as e:
        print(f"  ❌ isort 检查失败: {e}")
        return False


def run_isort_format(file_path: str) -> bool:
    """使用 isort 格式化导入"""
    try:
        tool_path = get_tool_path("isort")
        result = subprocess.run([tool_path, file_path], capture_output=True, text=True)
        # isort 会在 stderr 中输出 "Fixing" 信息
        if "Fixing" in result.stderr or result.stderr.strip():
            print(f"  🔧 isort: 已排序导入")
            return True
        return False
    except Exception as e:
        print(f"  ❌ isort 格式化失败: {e}")
        return False


def run_black_format(file_path: str, line_length: int = 88) -> bool:
    """使用 black 格式化代码"""
    try:
        tool_path = get_tool_path("black")
        result = subprocess.run(
            [tool_path, "--line-length", str(line_length), file_path],
            capture_output=True,
            text=True,
        )
        # Black 会在 stderr 中输出 "reformatted" 信息
        if "reformatted" in result.stderr or "would reformat" in result.stderr:
            print(f"  🔧 Black: 已格式化")
            return True
        return False
    except Exception as e:
        print(f"  ❌ Black 格式化失败: {e}")
        return False


def run_autopep8_format(file_path: str, line_length: int = 88) -> bool:
    """使用 autopep8 格式化代码"""
    try:
        tool_path = get_tool_path("autopep8")
        result = subprocess.run(
            [
                tool_path,
                "--in-place",
                "--aggressive",
                "--max-line-length",
                str(line_length),
                file_path,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  🔧 autopep8: 已格式化")
            return True
        return False
    except Exception as e:
        print(f"  ❌ autopep8 格式化失败: {e}")
        return False


def run_check_only(
    files: List[str], available_tools: List[str], args: argparse.Namespace
):
    """仅检查代码质量，不进行格式化"""
    issues_found = False

    for file_path in files:
        print(f"\n📄 检查文件: {file_path}")

        if "pylint" in available_tools and args.use_pylint:
            issues_found |= run_pylint_check(
                file_path, args.pylint_score, args.pylint_disable, args.pylint_config
            )

        if "black" in available_tools and args.use_black:
            issues_found |= run_black_check(file_path)

        if "isort" in available_tools and args.use_isort:
            issues_found |= run_isort_check(file_path)

    if issues_found:
        print(f"\n⚠️  发现代码质量问题，使用 gtools format 进行修复")
    else:
        print(f"\n✅ 所有文件都符合代码质量标准!")


def run_format(files: List[str], available_tools: List[str], args: argparse.Namespace):
    """执行代码格式化"""
    formatted_count = 0

    for file_path in files:
        print(f"\n📄 处理文件: {file_path}")
        file_changed = False

        # 使用 isort 排序导入
        if "isort" in available_tools and args.use_isort:
            if run_isort_format(file_path):
                file_changed = True

        # 使用 black 格式化代码
        if "black" in available_tools and args.use_black:
            if run_black_format(file_path, args.line_length):
                file_changed = True

        # 使用 autopep8 格式化（如果没有 black）
        if "autopep8" in available_tools and not args.use_black and args.use_autopep8:
            if run_autopep8_format(file_path, args.line_length):
                file_changed = True

        # 运行 pylint 检查（如果启用）
        if "pylint" in available_tools and args.use_pylint and not args.no_pylint_after:
            run_pylint_check(
                file_path, args.pylint_score, args.pylint_disable, args.pylint_config
            )

        if file_changed:
            formatted_count += 1
            print(f"  ✅ 已格式化")
        else:
            print(f"  📝 无需更改")

    print(f"\n🎉 格式化完成! 处理了 {formatted_count}/{len(files)} 个文件")


@FUNCTION.regist(module_name="format")
def main(args: argparse.Namespace):
    """代码格式化主函数"""
    print("🎨 代码格式化工具")

    # 获取目标路径
    target_path = args.path or "functions"
    if not os.path.isabs(target_path):
        target_path = os.path.join(os.getcwd(), target_path)

    if not os.path.exists(target_path):
        print(f"❌ 路径不存在: {target_path}")
        return

    # 查找 Python 文件
    python_files = find_python_files(target_path, args.recursive)

    if not python_files:
        print("📝 未找到 Python 文件")
        return

    print(f"📁 找到 {len(python_files)} 个 Python 文件")

    if args.list_files:
        print("\n📋 文件列表:")
        for file in python_files:
            print(f"  • {file}")
        return

    # 检查工具可用性
    available_tools = check_available_tools()
    print(f"🔧 可用工具: {', '.join(available_tools)}")

    if args.check_only:
        print("\n🔍 代码质量检查模式...")
        run_check_only(python_files, available_tools, args)
    else:
        print("\n✨ 代码格式化模式...")
        run_format(python_files, available_tools, args)


@ARGS.regist(module_name="format")
def parse_args():
    """参数解析函数"""
    parser = argparse.ArgumentParser(
        description="Python 代码格式化和质量检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  gtools format                         # 格式化 functions/ 目录
  gtools format --path src/             # 格式化指定目录
  gtools format --check-only            # 仅检查，不格式化
  gtools format --list-files            # 列出将要处理的文件
  gtools format --pylint-score 7.0      # 设置 pylint 最低评分
  gtools format --pylint-config .pylintrc  # 使用自定义配置文件
  
# 忽略特定检查项:
  gtools format --pylint-disable missing-docstring unused-import
  
# 不使用默认忽略规则:
  gtools format --pylint-disable

支持的工具:
  • pylint   - 代码质量检查 (支持忽略规则)
  • black    - 代码格式化
  • isort    - 导入排序
  • autopep8 - PEP8 格式化

默认忽略的 pylint 检查:
  • unused-import             - 未使用的导入
  • f-string-without-interpolation - 无插值的f字符串
  • too-few-public-methods     - 公共方法过少
  • too-many-arguments         - 参数过多
        """,
    )

    # 位置参数
    parser.add_argument(
        "path", nargs="?", default="functions", help="要格式化的路径（默认: functions）"
    )

    # 基本选项
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=True,
        help="递归处理子目录（默认启用）",
    )

    parser.add_argument(
        "--check-only", "-c", action="store_true", help="仅检查代码质量，不进行格式化"
    )

    parser.add_argument(
        "--list-files", "-l", action="store_true", help="列出将要处理的文件"
    )

    # 工具开关
    parser.add_argument(
        "--use-pylint",
        action="store_true",
        default=True,
        help="使用 pylint 检查（默认启用）",
    )

    parser.add_argument(
        "--use-black",
        action="store_true",
        default=True,
        help="使用 black 格式化（默认启用）",
    )

    parser.add_argument(
        "--use-isort",
        action="store_true",
        default=True,
        help="使用 isort 排序导入（默认启用）",
    )

    parser.add_argument(
        "--use-autopep8",
        action="store_true",
        help="使用 autopep8 格式化（当不使用 black 时）",
    )

    # 工具参数
    parser.add_argument(
        "--line-length", type=int, default=88, help="代码行长度限制（默认: 88）"
    )

    parser.add_argument(
        "--pylint-score",
        type=float,
        default=8.0,
        help="Pylint 最低评分要求（默认: 8.0）",
    )

    parser.add_argument(
        "--no-pylint-after", action="store_true", help="格式化后不运行 pylint 检查"
    )

    parser.add_argument(
        "--pylint-disable",
        nargs="*",
        default=[
            "unused-import",
            "f-string-without-interpolation",
            "too-few-public-methods",
            "too-many-arguments",
        ],
        help="要禁用的 pylint 检查项（默认禁用常见的不重要警告）",
    )

    parser.add_argument("--pylint-config", type=str, help="自定义 pylint 配置文件路径")

    return parser
