"""
注册机制的完整实现
包含：Registry类、配置处理、工具函数和全局实例
"""
import json
import os
import sys
import subprocess
import importlib
import argparse
from typing import Dict, Callable, Any, Optional, List


class Registry:
    """通用注册器类"""
    
    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, Any] = {}
        
    def regist(self, module_name: str):
        """装饰器：注册函数到指定模块名下"""
        def decorator(func: Callable):
            if module_name in self._registry:
                print(f"Warning: {module_name} already registered in {self.name}, overwriting...")
            self._registry[module_name] = func
            return func
        return decorator
    
    def get(self, module_name: str) -> Optional[Any]:
        """获取注册的函数"""
        return self._registry.get(module_name)
    
    def list_modules(self) -> list:
        """列出所有已注册的模块名"""
        return list(self._registry.keys())
    
    def has(self, module_name: str) -> bool:
        """检查模块是否已注册"""
        return module_name in self._registry


class ConfigHandler:
    """配置文件处理器"""
    
    @staticmethod
    def load_config(config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(config_file):
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")
            return {}
    
    @staticmethod
    def get_default_config_path(module_name: str) -> str:
        """获取默认配置文件路径"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "configs", module_name, "default.json")
    
    @staticmethod
    def merge_configs(default_config: Dict[str, Any], override_args: argparse.Namespace) -> argparse.Namespace:
        """合并默认配置和命令行参数"""
        merged_args = argparse.Namespace(**default_config)
        
        for key, value in vars(override_args).items():
            if value is not None:
                setattr(merged_args, key, value)
        
        return merged_args


def auto_import_functions_modules():
    """自动导入 functions 目录下的功能模块"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    functions_dir = os.path.join(base_dir, "functions")
    
    if not os.path.exists(functions_dir):
        return
    
    sys.path.insert(0, base_dir)
    
    for item in os.listdir(functions_dir):
        item_path = os.path.join(functions_dir, item)
        if os.path.isdir(item_path) and not item.startswith('_'):
            module_file = os.path.join(item_path, "main.py")
            if os.path.exists(module_file):
                try:
                    module_name = f"functions.{item}.main"
                    importlib.import_module(module_name)
                except ImportError as e:
                    print(f"Warning: Failed to import {module_name}: {e}")


def get_project_root() -> str:
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(__file__))


def get_module_info(module_name: str) -> Dict[str, Any]:
    """获取模块的完整信息"""
    info = {
        "module_name": module_name,
        "has_function": FUNCTION.has(module_name),
        "has_args": ARGS.has(module_name),
        "function": FUNCTION.get(module_name),
        "args_parser": ARGS.get(module_name),
        "has_start_sh": get_module_start_sh_path(module_name) is not None,
    }
    return info


def list_all_modules() -> list:
    """列出所有已注册的模块"""
    function_modules = set(FUNCTION.list_modules())
    args_modules = set(ARGS.list_modules())
    all_modules = function_modules.union(args_modules)
    return sorted(list(all_modules))


def validate_module(module_name: str) -> bool:
    """验证模块是否完整注册（既有函数又有参数解析器）"""
    return FUNCTION.has(module_name) and ARGS.has(module_name)


def list_modules_with_start_sh() -> List[str]:
    """列出所有包含start.sh文件的模块"""
    modules_with_start = []
    base_dir = os.path.dirname(os.path.dirname(__file__))
    functions_dir = os.path.join(base_dir, "functions")
    
    if not os.path.exists(functions_dir):
        return modules_with_start
    
    for item in os.listdir(functions_dir):
        item_path = os.path.join(functions_dir, item)
        if os.path.isdir(item_path) and not item.startswith('_'):
            start_sh_path = os.path.join(item_path, "start.sh")
            if os.path.exists(start_sh_path):
                modules_with_start.append(item)
    
    return sorted(modules_with_start)


def get_module_start_sh_path(module_name: str) -> Optional[str]:
    """获取指定模块的start.sh文件路径，如果不存在则返回None"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    functions_dir = os.path.join(base_dir, "functions")
    start_sh_path = os.path.join(functions_dir, module_name, "start.sh")
    
    if os.path.exists(start_sh_path):
        return start_sh_path
    return None


def execute_start_sh(module_name: str, args: List[str] = None) -> bool:
    """执行指定模块的start.sh脚本，并传递参数"""
    if args is None:
        args = []
        
    start_sh_path = get_module_start_sh_path(module_name)
    
    if not start_sh_path:
        print(f"错误: 模块 '{module_name}' 不包含 start.sh 文件")
        return False
    
    # 检查文件是否可执行
    if not os.access(start_sh_path, os.X_OK):
        print(f"警告: {start_sh_path} 文件不可执行，尝试添加执行权限...")
        try:
            os.chmod(start_sh_path, 0o755)
            print("✓ 已添加执行权限")
        except OSError as e:
            print(f"错误: 无法添加执行权限: {e}")
            return False
    
    # 设置工作目录为模块目录
    module_dir = os.path.dirname(start_sh_path)
    
    try:
        # 构建命令，将参数传递给脚本
        command = [start_sh_path] + args
        
        # 执行脚本
        result = subprocess.run(
            command,
            cwd=module_dir,
            capture_output=False,  # 不捕获输出，直接显示在控制台
            text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"✗ 脚本执行失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"错误: 执行脚本时发生异常: {e}")
        return False


# 全局注册实例
FUNCTION = Registry("FUNCTION")
ARGS = Registry("ARGS")