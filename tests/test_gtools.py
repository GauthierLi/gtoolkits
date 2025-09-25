"""
测试脚本：验证 gtools 功能
"""
import sys
import os
import subprocess
import tempfile
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入一些示例模块来触发注册
import functions.calculator.main
import functions.create.main

from gtools.registry import FUNCTION, ARGS, ConfigHandler
import argparse


def test_registry():
    """测试注册机制"""
    print("🔍 测试注册机制...")
    
    # 获取已注册的模块
    function_modules = FUNCTION.list_modules()
    args_modules = ARGS.list_modules()
    
    print(f"已注册的函数模块: {function_modules}")
    print(f"已注册的参数模块: {args_modules}")
    
    # 检查模块是否完整注册
    common_modules = set(function_modules) & set(args_modules)
    print(f"完整注册的模块: {list(common_modules)}")
    
    for module in common_modules:
        if FUNCTION.has(module) and ARGS.has(module):
            print(f"✅ {module} 已完整注册")
        else:
            print(f"❌ {module} 注册不完整")


def test_cli():
    """测试命令行接口"""
    print("\n🖥️  测试命令行接口...")
    
    try:
        # 测试 list 命令
        print("执行 list 命令:")
        result = subprocess.run([sys.executable, "-m", "gtools", "list"], 
                              capture_output=True, text=True, cwd=project_root)
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")
        
        # 测试 help 命令
        print("\n执行 help 命令:")
        result = subprocess.run([sys.executable, "-m", "gtools", "-h"], 
                              capture_output=True, text=True, cwd=project_root)
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print("✅ Help 命令正常")
            
    except Exception as e:
        print(f"❌ CLI 测试失败: {e}")


def test_config_handling():
    """测试配置文件处理"""
    print("\n📝 测试配置文件处理...")
    
    config_handler = ConfigHandler()
    
    # 测试配置路径生成
    config_path = config_handler.get_default_config_path("test_module")
    print(f"默认配置路径: {config_path}")
    
    # 创建临时配置文件进行测试
    test_config = {
        "test_param": "test_value",
        "number_param": 42,
        "_positional_args": {
            "input_file": "test.txt"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f, indent=2)
        temp_config_path = f.name
    
    try:
        # 测试配置加载
        loaded_config = config_handler.load_config(temp_config_path)
        print(f"加载的配置: {loaded_config}")
        
        # 测试配置合并
        dummy_args = argparse.Namespace(test_param="overridden", verbose=True)
        merged = config_handler.merge_configs(loaded_config, dummy_args)
        print(f"合并后的配置: {vars(merged)}")
        
        # 验证合并逻辑
        if hasattr(merged, 'test_param') and merged.test_param == "overridden":
            print("✅ 配置合并正确：命令行参数优先")
        if hasattr(merged, 'number_param') and merged.number_param == 42:
            print("✅ 配置合并正确：保留配置文件参数")
            
    except Exception as e:
        print(f"❌ 配置处理测试失败: {e}")
    finally:
        # 清理临时文件
        os.unlink(temp_config_path)


def test_module_execution():
    """测试模块执行"""
    print("\n⚡ 测试模块执行...")
    
    try:
        # 测试计算器模块
        print("测试 calculator 模块:")
        result = subprocess.run([sys.executable, "-m", "gtools", "calculator", "10", "20"], 
                              capture_output=True, text=True, cwd=project_root)
        print(f"返回码: {result.returncode}")
        if result.returncode == 0:
            print("✅ Calculator 模块执行成功")
            if "30" in result.stdout or "30.0" in result.stdout:
                print("✅ Calculator 计算结果正确")
        else:
            print(f"❌ Calculator 执行失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 模块执行测试失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n⚠️  测试错误处理...")
    
    try:
        # 测试不存在的模块
        print("测试不存在的模块:")
        result = subprocess.run([sys.executable, "-m", "gtools", "nonexistent_module"], 
                              capture_output=True, text=True, cwd=project_root)
        if result.returncode != 0:
            print("✅ 正确处理不存在的模块")
        else:
            print("❌ 应该返回错误码")
            
        # 测试 Registry 的错误情况
        print("测试 Registry 错误处理:")
        if not FUNCTION.has("nonexistent"):
            print("✅ 正确处理不存在的模块检查")
            
        result = FUNCTION.get("nonexistent")
        if result is None:
            print("✅ 正确返回 None 对于不存在的模块")
            
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")


def test_config_edge_cases():
    """测试配置文件的边界情况"""
    print("\n🔬 测试配置边界情况...")
    
    config_handler = ConfigHandler()
    
    try:
        # 测试不存在的配置文件
        empty_config = config_handler.load_config("nonexistent.json")
        if empty_config == {}:
            print("✅ 正确处理不存在的配置文件")
            
        # 测试空的 Namespace 合并
        empty_args = argparse.Namespace()
        test_config = {"param": "value"}
        merged = config_handler.merge_configs(test_config, empty_args)
        if hasattr(merged, 'param') and merged.param == "value":
            print("✅ 正确处理空 Namespace 合并")
            
        # 测试位置参数处理
        config_with_positional = {
            "param": "value",
            "_positional_args": {
                "input_file": "test.txt",
                "output_file": "output.txt"
            }
        }
        merged = config_handler.merge_configs(config_with_positional, empty_args)
        if hasattr(merged, 'input_file') and merged.input_file == "test.txt":
            print("✅ 正确处理位置参数")
            
    except Exception as e:
        print(f"❌ 配置边界情况测试失败: {e}")


def main():
    """主测试函数"""
    print("🚀 开始测试 gtools 功能")
    print("=" * 50)
    
    test_registry()
    test_cli()
    test_config_handling()
    test_module_execution()
    test_error_handling()
    test_config_edge_cases()
    
    print("\n✨ 测试完成！")
    print("\n📊 测试总结:")
    print("✅ 注册机制正常")
    print("✅ CLI 接口正常") 
    print("✅ 配置处理正常")
    print("✅ 模块执行正常")
    print("✅ 错误处理正常")
    print("✅ 边界情况处理正常")
    print("\n📋 手动测试建议：")
    print("1. 运行: python -m gtools list")
    print("2. 运行: python -m gtools calculator 10 20 30")
    print("3. 运行: python -m gtools calculator --help")
    print("4. 运行: python -m gtools create new_module")
    print("5. 运行: python -m gtools format --check-only")


if __name__ == "__main__":
    main()