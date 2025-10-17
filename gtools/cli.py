"""
命令行接口实现
"""
import sys
import os
import argparse
import traceback
import json
from typing import List, Optional
from beautifultable import BeautifulTable

from .registry import (
    FUNCTION, 
    ARGS, 
    ConfigHandler,
    get_module_info, 
    list_all_modules, 
    validate_module,
    auto_import_functions_modules,
    list_modules_with_start_sh,
    execute_start_sh,
    get_module_start_sh_path
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
  gtools module_name start                 # 执行模块的start.sh脚本
  gtools module_name start arg1 arg2       # 执行模块的start.sh脚本并传递参数
  gtools list                             # 列出所有可用模块
  gtools info module_name                 # 显示模块详细信息
            """.strip()
        )
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        list_parser = subparsers.add_parser('list', help='列出所有已注册的模块')
        
        info_parser = subparsers.add_parser('info', help='显示模块详细信息')
        info_parser.add_argument('module_name', help='模块名称')
        
        run_parser = subparsers.add_parser('run', help='运行配置文件指定的模块管道')
        run_parser.add_argument('--config', required=True, help='配置文件路径')
        
        return parser
    
    def handle_list_command(self):
        """处理 list 命令"""
        modules = list_all_modules()
        if not modules:
            print("没有找到已注册的模块")
            return
        
        print("已注册的模块:")
        print("-" * 70)
        
        # 创建美化表格
        table = BeautifulTable()
        table.columns.header = ["模块名", "注册状态", "start.sh"]
        
        # 添加表格数据
        for module in modules:
            is_complete = validate_module(module)
            has_start_sh = get_module_start_sh_path(module) is not None
            
            status = "✓ 完整" if is_complete else "✗ 不完整"
            start_sh_status = "✓ 有" if has_start_sh else "✗ 无"
            
            table.rows.append([module, status, start_sh_status])
        
        # 设置表格样式
        table.set_style(BeautifulTable.STYLE_GRID)
        table.columns.alignment['模块名'] = BeautifulTable.ALIGN_LEFT
        table.columns.alignment['注册状态'] = BeautifulTable.ALIGN_CENTER
        table.columns.alignment['start.sh'] = BeautifulTable.ALIGN_CENTER
        
        print(table)
        print(f"\n总计: {len(modules)} 个模块")
        print("说明:")
        print("  • 注册状态: ✓ 表示模块完整注册（有函数和参数解析器），✗ 表示注册不完整")
        print("  • start.sh: ✓ 表示模块包含启动脚本，✗ 表示无启动脚本")
        print("  • 使用 'gtools <module_name> start' 执行包含启动脚本的模块")
    
    def handle_info_command(self, module_name: str):
        """处理 info 命令"""
        info = get_module_info(module_name)
        
        print(f"模块信息: {module_name}")
        print("-" * 50)
        
        # 创建美化表格
        table = BeautifulTable()
        table.columns.header = ["属性", "状态"]
        
        # 添加表格数据
        table.rows.append(["函数已注册", "✓ 是" if info['has_function'] else "✗ 否"])
        table.rows.append(["参数解析器已注册", "✓ 是" if info['has_args'] else "✗ 否"])
        table.rows.append(["包含 start.sh", "✓ 是" if info['has_start_sh'] else "✗ 否"])
        table.rows.append(["模块完整性", "✓ 完整" if validate_module(module_name) else "✗ 不完整"])
        
        # 配置文件信息
        config_path = self.config_handler.get_default_config_path(module_name)
        config_exists = os.path.exists(config_path)
        table.rows.append(["配置文件存在", "✓ 是" if config_exists else "✗ 否"])
        
        # 设置表格样式
        table.set_style(BeautifulTable.STYLE_GRID)
        table.columns.alignment['属性'] = BeautifulTable.ALIGN_LEFT
        table.columns.alignment['状态'] = BeautifulTable.ALIGN_CENTER
        
        print(table)
        
        # 显示配置文件信息
        if config_exists:
            print(f"\n配置文件路径: {config_path}")
        
        if info['has_start_sh']:
            start_sh_path = get_module_start_sh_path(module_name)
            print(f"start.sh 路径: {start_sh_path}")
            print("使用命令: gtools {} start".format(module_name))
    
    def build_execution_order(self, modules: List[dict]) -> List[str]:
        """构建模块执行顺序，支持依赖关系"""
        from collections import defaultdict, deque
        
        # 检查是否有依赖
        has_dependencies = any('depends_on' in module for module in modules)
        if not has_dependencies:
            # 无依赖，按配置顺序执行
            return [m['name'] for m in modules]
        
        # 构建图
        graph = defaultdict(list)  # module -> list of modules that depend on it
        in_degree = defaultdict(int)
        module_names = [m['name'] for m in modules]
        
        for module in modules:
            name = module['name']
            in_degree[name] = 0  # 初始化
        
        for module in modules:
            name = module['name']
            if 'depends_on' in module:
                for dep in module['depends_on']:
                    if dep not in module_names:
                        raise ValueError(f"模块 '{name}' 的依赖 '{dep}' 不存在")
                    graph[dep].append(name)
                    in_degree[name] += 1
        
        # 拓扑排序
        queue = deque([name for name in module_names if in_degree[name] == 0])
        execution_order = []
        
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(execution_order) != len(module_names):
            raise ValueError("模块依赖关系存在环，无法确定执行顺序")
        
        return execution_order
    
    def handle_run_command(self, config_path: str):
        """处理 run 命令"""
        if not os.path.exists(config_path):
            print(f"错误: 配置文件 '{config_path}' 不存在")
            sys.exit(1)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件 JSON 格式错误: {e}")
            sys.exit(1)
        
        # 验证配置
        if 'working_directory' not in config:
            print("错误: 配置中缺少 'working_directory'")
            sys.exit(1)
        
        working_dir = config['working_directory']
        if not os.path.exists(working_dir):
            print(f"错误: 工作目录 '{working_dir}' 不存在")
            sys.exit(1)
        
        if 'modules' not in config or not isinstance(config['modules'], list):
            print("错误: 配置中缺少 'modules' 列表")
            sys.exit(1)
        
        modules = config['modules']
        if not modules:
            print("错误: modules 列表为空")
            sys.exit(1)
        
        # 验证模块
        for module in modules:
            if 'name' not in module:
                print(f"错误: 模块配置缺少 'name': {module}")
                sys.exit(1)
            name = module['name']
            if not FUNCTION.has(name):
                print(f"错误: 模块 '{name}' 未注册")
                sys.exit(1)
        
        # 检查依赖（简单检查，无环）
        module_names = [m['name'] for m in modules]
        for module in modules:
            if 'depends_on' in module:
                for dep in module['depends_on']:
                    if dep not in module_names:
                        print(f"错误: 模块 '{module['name']}' 的依赖 '{dep}' 不存在")
                        sys.exit(1)
        
        # 检查依赖（构建DAG并拓扑排序）
        execution_order = self.build_execution_order(modules)
        
        # 切换到工作目录
        original_dir = os.getcwd()
        os.chdir(working_dir)
        
        try:
            print(f"切换到工作目录: {working_dir}")
            print("开始执行模块管道...")
            
            for i, module_name in enumerate(execution_order, 1):
                module = next(m for m in modules if m['name'] == module_name)
                params = module.get('params', {})
                
                print(f"\n[{i}/{len(execution_order)}] 执行模块: {module_name}")
                
                # 构建参数
                main_func = FUNCTION.get(module_name)
                args_parser_func = ARGS.get(module_name)
                
                temp_parser = args_parser_func()
                synthetic_args = []
                
                # 处理位置参数
                positional_config = params.get('_positional_args', {})
                for param_name, param_value in positional_config.items():
                    if isinstance(param_value, list):
                        synthetic_args.extend(map(str, param_value))
                    else:
                        synthetic_args.append(str(param_value))
                
                # 处理可选参数
                for key, value in params.items():
                    if key == '_positional_args':
                        continue
                    
                    # 查找对应的 action 来确定如何构建参数
                    for action in temp_parser._actions:
                        if action.dest == key and action.option_strings:
                            if isinstance(action, argparse._StoreTrueAction) and value:
                                synthetic_args.append(action.option_strings[0])
                            elif not isinstance(action, argparse._StoreTrueAction):
                                synthetic_args.extend([action.option_strings[0], str(value)])
                            break
                
                # 解析参数
                if synthetic_args:
                    parsed_args = temp_parser.parse_args(synthetic_args)
                else:
                    parsed_args = temp_parser.parse_args([])
                
                # 执行模块
                main_func(parsed_args)
                
                print(f"模块 '{module_name}' 执行完成")
            
            print("\n✅ 所有模块执行完成")
            
        except Exception as e:
            print(f"\n❌ 执行过程中出错: {e}")
            traceback.print_exc()
            sys.exit(1)
        finally:
            os.chdir(original_dir)
    
    def handle_module_start(self, module_name: str, args: List[str] = None):
        """处理模块的 start 命令"""
        if args is None:
            args = []
        success = execute_start_sh(module_name, args)
        if not success:
            sys.exit(1)
    
    def run_module(self, module_name: str, args: List[str]):
        """运行指定的模块"""
        if not validate_module(module_name):
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
            parsed_args = None
            
            # 如果没有提供命令行参数但有默认配置，直接使用配置构建参数
            if not args and default_config:
                synthetic_args = []
                
                # 处理位置参数 - 从 _positional_args 中获取（如果存在）
                positional_config = default_config.get('_positional_args', {})
                for param_name, param_value in positional_config.items():
                    if isinstance(param_value, list):
                        synthetic_args.extend(map(str, param_value))
                    else:
                        synthetic_args.append(str(param_value))
                
                # 处理可选参数 - 除了 _positional_args 外的其他键
                for key, value in default_config.items():
                    if key == '_positional_args':
                        continue
                    
                    # 查找对应的 action 来确定如何构建参数
                    for action in temp_parser._actions:
                        if action.dest == key and action.option_strings:
                            if isinstance(action, argparse._StoreTrueAction) and value:
                                synthetic_args.append(action.option_strings[0])
                            elif not isinstance(action, argparse._StoreTrueAction):
                                synthetic_args.extend([action.option_strings[0], str(value)])
                            break
                
                # 使用合成的参数进行解析
                if synthetic_args:
                    parsed_args = temp_parser.parse_args(synthetic_args)
                else:
                    # 如果没有合成参数，尝试正常解析
                    parsed_args = temp_parser.parse_args(args)
            else:
                # 有命令行参数或没有默认配置，正常解析
                parsed_args = temp_parser.parse_args(args)
            
            # 合并配置时需要处理新的配置结构
            final_config = {}
            if default_config:
                # 将位置参数配置展开到顶层（如果存在）
                if '_positional_args' in default_config:
                    final_config.update(default_config['_positional_args'])
                # 添加其他配置项
                for key, value in default_config.items():
                    if key != '_positional_args':
                        final_config[key] = value
            
            final_args = self.config_handler.merge_configs(final_config, parsed_args)
            
            print(f"运行模块: {module_name}")
            main_func(final_args)
            
        except Exception as e:
            print(f"\n❌ 运行模块 '{module_name}' 时出错:")
            print(f"错误信息: {e}")
            print("\n详细错误追踪:")
            print("-" * 50)
            traceback.print_exc()
            print("-" * 50)
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
        
        # 检查是否是帮助命令
        if argv[0] in ['-h', '--help']:
            parser = self.create_main_parser()
            parser.print_help()
            return
        
        # 检查是否是子命令格式 (list, info, run)
        if len(argv) >= 1 and argv[0] in ['list', 'info', 'run']:
            parser = self.create_main_parser()
            try:
                args = parser.parse_args(argv)
                
                if args.command == 'list':
                    self.handle_list_command()
                    return
                
                if args.command == 'info':
                    self.handle_info_command(args.module_name)
                    return
                
                if args.command == 'run':
                    self.handle_run_command(args.config)
                    return
            except SystemExit:
                # argparse 会在遇到错误时调用 sys.exit，我们需要捕获它
                sys.exit(1)
        
        # 检查是否是 gtools <module_name> start [args...] 格式
        if len(argv) >= 2 and argv[1] == 'start':
            module_name = argv[0]
            start_args = argv[2:]  # start 后面的所有参数
            self.handle_module_start(module_name, start_args)
            return
        
        # 如果不是已知的子命令，则作为模块名处理
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