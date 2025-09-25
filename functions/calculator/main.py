"""
计算器模块：演示更复杂的功能实现
"""

import argparse

from gtools.registry import ARGS, FUNCTION


@FUNCTION.regist(module_name="calculator")
def main(args: argparse.Namespace):
    """计算器主函数"""
    print("🧮 计算器模块")

    if args.operation == "add":
        result = sum(args.numbers)
        print(f"{' + '.join(map(str, args.numbers))} = {result}")

    elif args.operation == "multiply":
        result = 1
        for num in args.numbers:
            result *= num
        print(f"{' × '.join(map(str, args.numbers))} = {result}")

    elif args.operation == "average":
        if args.numbers:
            result = sum(args.numbers) / len(args.numbers)
            print(f"平均值: {result:.2f}")
        else:
            print("错误: 需要至少一个数字")

    if args.show_details:
        print(f"输入数字: {args.numbers}")
        print(f"操作类型: {args.operation}")


@ARGS.regist(module_name="calculator")
def parse_args():
    """计算器参数解析"""
    parser = argparse.ArgumentParser(
        description="简单计算器", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("numbers", nargs="+", type=float, help="要计算的数字列表")

    parser.add_argument(
        "--operation",
        "-op",
        choices=["add", "multiply", "average"],
        default="add",
        help="计算操作类型 (默认: add)",
    )

    parser.add_argument(
        "--show-details", "-d", action="store_true", help="显示详细信息"
    )

    return parser
