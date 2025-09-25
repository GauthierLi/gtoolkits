"""
{MODULE_NAME_TITLE} 模块：请在这里描述模块的功能
"""

import argparse

from gtools.registry import ARGS, FUNCTION

MODULE_NAME = "MODULE_NAME"


@FUNCTION.regist(module_name=f"{MODULE_NAME}")
def main(args: argparse.Namespace):
    f"""主函数：{MODULE_NAME} 模块的主要逻辑"""
    print(f"🔧 {MODULE_NAME} 模块执行中...")
    print(f"参数信息: {args}")

    print("✅ 执行完成！")


@ARGS.regist(module_name="{MODULE_NAME}")
def parse_args():
    f"""参数解析函数：定义 {MODULE_NAME} 模块接受的参数"""
    parser = argparse.ArgumentParser(
        description="{MODULE_NAME_TITLE} 模块 - 请在这里描述模块功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
使用示例:
  gtools {MODULE_NAME}                          # 使用默认配置
  gtools {MODULE_NAME} --input-param value     # 指定输入参数
  gtools {MODULE_NAME} --debug                 # 启用调试模式
        """.strip(),
    )

    # TODO: 根据需要添加你的参数定义
    parser.add_argument(
        "--input-param",
        type=str,
        default="default_value",
        help="输入参数说明 (默认: default_value)",
    )

    parser.add_argument(
        "--debug", type=bool, default=False, help="调试模式 (默认: False)"
    )

    # 位置参数示例（如果需要的话）
    # parser.add_argument(
    #     "input_files",
    #     nargs="+",
    #     help="输入文件列表"
    # )

    return parser
