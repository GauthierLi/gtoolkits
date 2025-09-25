"""
Remove 模块：移除已存在的模块和配置文件
用法：gtools remove <module_name>
"""

import argparse
import shutil
from pathlib import Path

from gtools.registry import ARGS, FUNCTION

RESERVE_MODULES = {"create", "remove", "test_module", "calculator", "update"}


@FUNCTION.regist(module_name="remove")
def main(args: argparse.Namespace):
    """主函数：移除指定的模块和配置"""
    # 如果请求列出模块
    if args.list:
        list_removable_modules()
        return

    # 如果没有提供模块名且不是列出操作
    if not args.module_name:
        print("❌ 请提供要删除的模块名称，或使用 --list 查看可删除的模块")
        print("💡 使用方法: gtools remove <module_name> 或 gtools remove --list")
        return

    module_name = args.module_name

    # 检查是否是系统保留模块
    reserved_modules = RESERVE_MODULES
    if module_name in reserved_modules:
        print(f"❌ 不能删除系统保留模块: {module_name}")
        print(f"保留模块列表: {', '.join(sorted(reserved_modules))}")
        return

    base_dir = Path(__file__).parent.parent.parent
    module_dir = base_dir / "functions" / module_name
    config_dir = base_dir / "configs" / module_name

    # 检查模块是否存在
    module_exists = module_dir.exists()
    config_exists = config_dir.exists()

    if not module_exists and not config_exists:
        print(f"❌ 模块 '{module_name}' 不存在！")
        return

    # 显示要删除的内容
    print(f"🗑️  准备删除模块: {module_name}")
    if module_exists:
        print(f"📂 模块目录: {module_dir}")
    if config_exists:
        print(f"⚙️  配置目录: {config_dir}")

    # 安全确认
    if not args.force:
        print(f"\n⚠️  警告：此操作不可逆！")
        try:
            confirmation = (
                input(f"确认删除模块 '{module_name}' 吗？[y/N]: ").strip().lower()
            )
            if confirmation not in ["y", "yes"]:
                print("❌ 操作已取消")
                return
        except (KeyboardInterrupt, EOFError):
            print("\n❌ 操作已取消")
            return

    try:
        removed_items = []

        # 删除模块目录
        if module_exists:
            shutil.rmtree(module_dir)
            removed_items.append(f"模块目录: {module_dir}")
            print(f"✅ 已删除模块目录: {module_dir}")

        # 删除配置目录
        if config_exists:
            shutil.rmtree(config_dir)
            removed_items.append(f"配置目录: {config_dir}")
            print(f"✅ 已删除配置目录: {config_dir}")

        print(f"\n🎉 模块 '{module_name}' 删除成功！")
        print(f"已删除 {len(removed_items)} 个项目:")
        for item in removed_items:
            print(f"  • {item}")

        if args.backup:
            print(f"\n💡 提示: 如需恢复，可以从备份中恢复（如果有的话）")

    except Exception as e:
        print(f"❌ 删除模块时发生错误: {e}")


def list_removable_modules():
    """列出所有可删除的模块"""
    base_dir = Path(__file__).parent.parent.parent
    functions_dir = base_dir / "functions"
    configs_dir = base_dir / "configs"

    reserved_modules = RESERVE_MODULES

    print("📋 可删除的模块列表:")
    print("=" * 50)

    # 获取所有模块
    all_modules = set()

    # 从 functions 目录获取
    if functions_dir.exists():
        for item in functions_dir.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and not item.name.startswith("__")
            ):  # 排除 __pycache__ 等
                all_modules.add(item.name)

    # 从 configs 目录获取
    if configs_dir.exists():
        for item in configs_dir.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and not item.name.startswith("__")
            ):  # 排除 __pycache__ 等
                all_modules.add(item.name)

    # 过滤掉保留模块
    removable_modules = all_modules - reserved_modules

    if not removable_modules:
        print("🔍 没有找到可删除的模块")
        print(f"💡 保留模块（不可删除）: {', '.join(sorted(reserved_modules))}")
        return

    for module_name in sorted(removable_modules):
        module_dir = functions_dir / module_name
        config_dir = configs_dir / module_name

        status_parts = []
        if module_dir.exists():
            status_parts.append("📂 模块")
        if config_dir.exists():
            status_parts.append("⚙️ 配置")

        status = " + ".join(status_parts) if status_parts else "❓ 未知"
        print(f"  • {module_name:<20} ({status})")

    print(f"\n📊 统计:")
    print(f"  • 可删除模块: {len(removable_modules)} 个")
    print(f"  • 保留模块: {len(reserved_modules)} 个")
    print(f"\n💡 使用方法: gtools remove <module_name>")


@ARGS.regist(module_name="remove")
def parse_args():
    """参数解析函数：定义 remove 模块接受的参数"""
    parser = argparse.ArgumentParser(
        description="Remove 模块 - 移除已存在的模块和配置文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  gtools remove --list                 # 列出所有可删除的模块
  gtools remove my_module              # 移除模块（需要确认）
  gtools remove my_module --force      # 强制移除（跳过确认）
  gtools remove my_module --backup     # 移除前创建备份
        """.strip(),
    )

    parser.add_argument(
        "module_name", nargs="?", help="要删除的模块名称"  # 可选的位置参数
    )

    parser.add_argument(
        "--force", "-f", action="store_true", help="强制删除，跳过确认提示"
    )

    parser.add_argument(
        "--backup", "-b", action="store_true", help="删除前创建备份（暂未实现）"
    )

    parser.add_argument(
        "--list", "-l", action="store_true", help="列出所有可删除的模块"
    )

    return parser
