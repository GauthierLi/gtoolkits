"""
配置文件处理相关的通用功能
"""
import json
import os
import argparse
from typing import Dict, Any


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
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "configs", module_name, "default.json")
    
    @staticmethod
    def merge_configs(default_config: Dict[str, Any], override_args: argparse.Namespace) -> argparse.Namespace:
        """合并默认配置和命令行参数"""
        merged_args = argparse.Namespace(**default_config)
        
        for key, value in vars(override_args).items():
            if value is not None:
                setattr(merged_args, key, value)
        
        return merged_args