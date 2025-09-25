"""
测试模块：演示如何使用注册机制
"""
import argparse
import time
from gtools.registry import FUNCTION, ARGS


@FUNCTION.regist(module_name='test_module')
def main(args: argparse.Namespace):
    """主函数：处理测试模块的逻辑"""
    print("=" * 50)
    print("测试模块执行中...")
    print(f"配置文件路径: {args.config_file}")
    print(f"输出目录: {args.output_dir}")
    print(f"详细模式: {args.verbose}")
    print(f"处理项目: {', '.join(args.items) if args.items else '无'}")
    
    if args.dry_run:
        print("🔄 这是一次试运行，不会执行实际操作")
    else:
        print("✅ 执行实际操作")
    
    print("正在处理...")
    time.sleep(1)
    
    print("✨ 测试模块执行完成！")
    print("=" * 50)


@ARGS.regist(module_name='test_module')
def parse_args():
    """参数解析函数：定义测试模块接受的参数"""
    parser = argparse.ArgumentParser(
        description="测试模块 - 演示注册机制的使用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  gtools test_module                           # 使用默认配置
  gtools test_module -c custom.json           # 指定配置文件
  gtools test_module -o /tmp/output -v        # 指定输出目录并启用详细模式
  gtools test_module --items item1 item2      # 处理特定项目
        """.strip()
    )
    
    parser.add_argument(
        "--config-file", "-c", 
        type=str, 
        default="default.json",
        help="配置文件路径 (默认: default.json)"
    )
    
    parser.add_argument(
        "--output-dir", "-o", 
        type=str, 
        default="/tmp/gtools_output",
        help="输出目录 (默认: /tmp/gtools_output)"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="启用详细输出模式"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="试运行模式，不执行实际操作"
    )
    
    parser.add_argument(
        "--items", 
        nargs="*",
        help="要处理的项目列表"
    )
    
    return parser