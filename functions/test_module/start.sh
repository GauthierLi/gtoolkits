#!/bin/bash

# Test Module启动脚本示例

echo "🧪 启动Test Module模块..."
echo "模块路径: $(pwd)"
echo "时间: $(date)"

# 显示接收到的参数
echo ""
if [ $# -gt 0 ]; then
    echo "接收到参数: $*"
else
    echo "无参数"
fi

echo ""
echo "这是一个测试模块的启动脚本示例"
echo "可以在这里添加模块特定的初始化逻辑"

# 根据参数执行不同的逻辑
echo ""
if [ $# -gt 0 ]; then
    echo "根据参数执行自定义逻辑:"
    case "$1" in
        "test")
            echo "  - 执行测试模式"
            ;;
        "debug")
            echo "  - 启用调试模式"
            ;;
        "info")
            echo "  - 显示详细信息"
            ;;
        *)
            echo "  - 未知参数 '$1'，使用默认模式"
            ;;
    esac
else
    echo "使用默认启动模式"
fi

echo ""
echo "模块信息:"
echo "  - 名称: test_module"  
echo "  - 用途: 演示gtools框架功能"
echo "  - 启动脚本: start.sh"

echo ""
echo "🎉 Test Module模块启动完成!"
echo "提示: 使用 'gtools test_module --help' 查看模块功能"