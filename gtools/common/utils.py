"""
通用工具函数
"""
import os
import sys
import importlib


def auto_import_functions_modules():
    """自动导入 functions 目录下的功能模块"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
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
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))