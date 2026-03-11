"""
Create 模块：自动生成新的算子模板
用法：gtools create <module_name>
"""

import argparse
import os
import shutil
from pathlib import Path

from gtools.registry import ARGS, FUNCTION


@FUNCTION.regist(module_name="create")
def main(args: argparse.Namespace):
    """主函数：创建新的算子模块"""
    module_name = args.module_name

    # 检查模块是否已存在
    base_dir = Path(__file__).parent.parent.parent
    module_dir = base_dir / "functions" / module_name

    if module_dir.exists():
        print(f"❌ 模块 '{module_name}' 已存在！")
        print(f"路径：{module_dir}")
        return

    print(f"🚀 开始创建新模块：{module_name}")
    print(f"📦 默认创建 OpenClaw 技能包模板 (SKILL.md)")

    try:
        # 获取模板文件路径
        template_dir = Path(__file__).parent / "reference"

        # 创建模块目录
        module_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录：{module_dir}")

        # 复制并处理 main.py 模板文件
        template_main = template_dir / "main.py"
        target_main = module_dir / "main.py"

        with open(template_main, "r", encoding="utf-8") as f:
            main_content = f.read()

        # 替换占位符
        main_content = replace_placeholders(main_content, module_name)

        with open(target_main, "w", encoding="utf-8") as f:
            f.write(main_content)
        print(f"✅ 创建文件：{target_main}")

        # 复制配置文件模板
        template_config = template_dir / "default.json"
        config_dir = base_dir / "configs" / module_name
        config_dir.mkdir(parents=True, exist_ok=True)

        target_config = config_dir / "default.json"
        shutil.copy2(template_config, target_config)
        print(f"✅ 创建配置文件：{target_config}")

        # 复制并处理 start.sh 模板文件
        template_start = template_dir / "start.sh"
        target_start = module_dir / "start.sh"

        with open(template_start, "r", encoding="utf-8") as f:
            start_content = f.read()

        # 替换占位符
        start_content = replace_placeholders(start_content, module_name)

        with open(target_start, "w", encoding="utf-8") as f:
            f.write(start_content)

        # 添加执行权限
        os.chmod(target_start, 0o755)
        print(f"✅ 创建启动脚本：{target_start}")

        # 创建 SKILL.md 模板（默认行为）
        template_skill = template_dir / "SKILL.md"
        if template_skill.exists():
            with open(template_skill, "r", encoding="utf-8") as f:
                skill_content = f.read()

            # 替换占位符
            skill_content = replace_placeholders(skill_content, module_name)

            target_skill = module_dir / "SKILL.md"
            with open(target_skill, "w", encoding="utf-8") as f:
                f.write(skill_content)
            print(f"✅ 创建技能包模板：{target_skill}")
        else:
            print(f"⚠️  警告：SKILL.md 模板文件不存在，跳过创建")

        print(f"\n🎉 模块 '{module_name}' 创建成功！")
        print(f"📂 模块路径：{module_dir}")
        print(f"⚙️  配置路径：{config_dir}")
        print(f"\n📖 使用方法:")
        print(f"   gtools {module_name}           # 使用默认配置运行")
        print(f"   gtools {module_name} start     # 执行启动脚本")
        print(f"   gtools {module_name} --help   # 查看帮助信息")
        
        print(f"\n🐱 技能包转换:")
        print(f"   1. 编辑 {module_dir}/SKILL.md 完善技能描述")
        print(f"   2. 参考 OpenClaw 技能包格式 (name, description 必填)")
        print(f"   3. 可添加 scripts/, references/, assets/ 目录")
        print(f"   4. 使用 OpenClaw 技能打包工具打包")
        
        print(f"\n📝 配置文件说明:")
        print(f'   • 位置参数配置：使用 "_positional_args" 字段')
        print(f'     例如："_positional_args": {{"files": ["file1.txt", "file2.txt"]}}')
        print(f"   • 可选参数配置：直接在顶层配置")
        print(f'     例如： "debug": true, "items": ["a", "b"]')
        print(f"   • 布尔参数：true/false")
        print(f'   • 列表参数：["item1", "item2"]')

    except Exception as e:
        print(f"❌ 创建模块时发生错误：{e}")


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


@ARGS.regist(module_name="create")
def parse_args():
    """参数解析函数：定义 create 模块接受的参数"""
    parser = argparse.ArgumentParser(
        description="Create 模块 - 自动生成新的算子模板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  gtools create my_module           # 创建名为 my_module 的新模块（默认包含 SKILL.md）
  gtools create data_processor      # 创建名为 data_processor 的新模块
        """.strip(),
    )

    parser.add_argument("module_name", help="要创建的模块名称")

    return parser
