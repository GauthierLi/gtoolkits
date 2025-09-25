"""
测试脚本：验证 gtools 功能
"""
import sys
import os
import subprocess

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import functions.test_module.main
import functions.calculator.main

from gtools.registry import FUNCTION, ARGS
from gtools.common import ConfigHandler, list_all_modules, validate_module
import argparse


def test_registry():
    """测试注册机制"""
    print("🔍 测试注册机制...")
    
    modules = list_all_modules(FUNCTION, ARGS)
    print(f"已注册模块: {modules}")
    
    for module in modules:
        if validate_module(FUNCTION, ARGS, module):
            print(f"✅ {module} 已完整注册")
        else:
            print(f"❌ {module} 注册不完整")


def test_cli():
    """测试命令行接口"""
    print("\n🖥️  测试命令行接口...")
    
    print("执行 list 命令:")
    from gtools.cli import CLI
    cli = CLI()
    cli.handle_list_command()
    
    print("\n执行 info 命令:")
    cli.handle_info_command("test_module")


def test_config_handling():
    """测试配置文件处理"""
    print("\n📝 测试配置文件处理...")
    
    config_handler = ConfigHandler()
    
    config_path = config_handler.get_default_config_path("test_module")
    print(f"默认配置路径: {config_path}")
    
    config = config_handler.load_config(config_path)
    print(f"加载的配置: {config}")
    
    dummy_args = argparse.Namespace(verbose=True, output_dir=None)
    merged = config_handler.merge_configs(config, dummy_args)
    print(f"合并后的配置: {vars(merged)}")


def main():
    """主测试函数"""
    print("🚀 开始测试 gtools 功能")
    print("=" * 50)
    
    test_registry()
    test_cli()
    test_config_handling()
    
    print("\n✨ 测试完成！")
    print("\n手动测试建议：")
    print("1. 运行: python -m gtools list")
    print("2. 运行: python -m gtools info test_module")
    print("3. 运行: python -m gtools test_module -h")
    print("4. 运行: python -m gtools test_module")
    print("5. 运行: python -m gtools calculator 10 20 30")


if __name__ == "__main__":
    main()