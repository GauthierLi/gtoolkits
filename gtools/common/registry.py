"""
通用注册器类
"""
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


def get_module_info(function_registry: Registry, args_registry: Registry, module_name: str) -> Dict[str, Any]:
    """获取模块的完整信息"""
    info = {
        "module_name": module_name,
        "has_function": function_registry.has(module_name),
        "has_args": args_registry.has(module_name),
        "function": function_registry.get(module_name),
        "args_parser": args_registry.get(module_name),
    }
    return info


def list_all_modules(function_registry: Registry, args_registry: Registry) -> list:
    """列出所有已注册的模块"""
    function_modules = set(function_registry.list_modules())
    args_modules = set(args_registry.list_modules())
    all_modules = function_modules.union(args_modules)
    return sorted(list(all_modules))


def validate_module(function_registry: Registry, args_registry: Registry, module_name: str) -> bool:
    """验证模块是否完整注册（既有函数又有参数解析器）"""
    return function_registry.has(module_name) and args_registry.has(module_name)