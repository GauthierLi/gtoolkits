"""
命令行接口实现
"""
import sys
import os
import argparse
from typing import List, Optional

from .registry import FUNCTION, ARGS
from .common import (
    get_module_info, 
    list_all_modules, 
    validate_module,
    ConfigHandler,
    auto_import_functions_modules
)


class CLI:
    """命令行接口类"""
    
    def __init__(self):
        self.config_handler = ConfigHandler()
    
    def create_main_parser(self) -> argparse.ArgumentParser:
        """创建主命令行解析器"""
        parser = argparse.ArgumentParser(
            prog='gtools',
            description='基于注册机制的功能调用和配置系统',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  gtools module_name -h                    # 显示模块帮助信息
  gtools module_name --param1 value1      # 运行模块并指定参数
  gtools list                             # 列出所有可用模块
  gtools info module_name                 # 显示模块详细信息
            """.strip()
        )
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        list_parser = subparsers.add_parser('list', help='列出所有已注册的模块')
        
        info_parser = subparsers.add_parser('info', help='显示模块详细信息')
        info_parser.add_argument('module_name', help='模块名称')
        
        return parser
    
    def handle_list_command(self):
        """处理 list 命令"""
        modules = list_all_modules(FUNCTION, ARGS)
        if not modules:
            print("没有找到已注册的模块")
            return
        
        print("已注册的模块:")
        for module in modules:
            status = "✓" if validate_module(FUNCTION, ARGS, module) else "✗"
            print(f"  {status} {module}")
        
        print(f"\n总计: {len(modules)} 个模块")
        print("说明: ✓ 表示模块完整注册（有函数和参数解析器），✗ 表示注册不完整")
    
    def handle_info_command(self, module_name: str):
        """处理 info 命令"""
        info = get_module_info(FUNCTION, ARGS, module_name)
        
        print(f"模块信息: {module_name}")
        print("-" * 40)
        print(f"函数已注册: {'是' if info['has_function'] else '否'}")
        print(f"参数解析器已注册: {'是' if info['has_args'] else '否'}")
        print(f"完整性: {'完整' if validate_module(FUNCTION, ARGS, module_name) else '不完整'}")
        
        config_path = self.config_handler.get_default_config_path(module_name)
        config_exists = os.path.exists(config_path)
        print(f"默认配置文件: {config_path}")
        print(f"配置文件存在: {'是' if config_exists else '否'}")
    
    def run_module(self, module_name: str, args: List[str]):
        """运行指定的模块"""
        if not validate_module(FUNCTION, ARGS, module_name):
            print(f"错误: 模块 '{module_name}' 未完整注册")
            if not FUNCTION.has(module_name):
                print(f"  缺少函数注册，请使用 @FUNCTION.regist(module_name='{module_name}')")
            if not ARGS.has(module_name):
                print(f"  缺少参数解析器注册，请使用 @ARGS.regist(module_name='{module_name}')")
            sys.exit(1)
        
        main_func = FUNCTION.get(module_name)
        args_parser_func = ARGS.get(module_name)
        
        try:
            config_path = self.config_handler.get_default_config_path(module_name)
            default_config = self.config_handler.load_config(config_path)
            
            temp_parser = args_parser_func()
            
            try:
                parsed_args = temp_parser.parse_args(args)
            except SystemExit as e:
                sys.exit(e.code)
            
            final_args = self.config_handler.merge_configs(default_config, parsed_args)
            
            print(f"运行模块: {module_name}")
            main_func(final_args)
            
        except Exception as e:
            print(f"运行模块 '{module_name}' 时出错: {e}")
            sys.exit(1)
    
    def auto_import_modules(self):
        """自动导入可能包含注册函数的模块"""
        auto_import_functions_modules()
    
    def main(self, argv: Optional[List[str]] = None):
        """主入口函数"""
        if argv is None:
            argv = sys.argv[1:]
        
        self.auto_import_modules()
        
        if not argv:
            parser = self.create_main_parser()
            parser.print_help()
            return
        
        if argv[0] == 'list':
            self.handle_list_command()
            return
        
        if argv[0] == 'info' and len(argv) >= 2:
            self.handle_info_command(argv[1])
            return
        
        module_name = argv[0]
        module_args = argv[1:]
        
        if FUNCTION.has(module_name) or ARGS.has(module_name):
            self.run_module(module_name, module_args)
            return
        
        print(f"未知命令或模块: {module_name}")
        print("使用 'gtools list' 查看可用模块")
        print("使用 'gtools -h' 查看帮助信息")
        sys.exit(1)


def main():
    """命令行入口点"""
    cli = CLI()
    cli.main()