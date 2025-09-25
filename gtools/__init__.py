"""
gtool_registry_version - 基于注册机制的功能调用和配置系统
"""

__version__ = "1.0.0"
__author__ = "gtools team"
__description__ = "A registry-based function calling and configuration system"

from .registry import FUNCTION, ARGS

__all__ = ["FUNCTION", "ARGS"]