"""
注册机制的完整实现
包含：Registry类、配置处理、工具函数和全局实例
"""
import json
import os
import sys
import importlib
import argparse
from typing import Dict, Callable, Any, Optional


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


# 全局注册实例
FUNCTION = Registry("FUNCTION")
ARGS = Registry("ARGS")