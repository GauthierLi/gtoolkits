#!/bin/bash

# Calculator模块启动脚本示例
# 这个脚本演示如何在模块中使用start.sh以及如何接收参数

echo "🧮 启动Calculator模块..."
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
echo "检查Python环境..."
if command -v python3 &> /dev/null; then
    echo "✓ Python3 已安装: $(python3 --version)"
else
    echo "✗ Python3 未找到"
    exit 1
fi

echo ""
echo "检查所需文件..."
if [[ -f "main.py" ]]; then
    echo "✓ main.py 存在"
else
    echo "✗ main.py 不存在"
    exit 1
fi

echo ""
echo "运行示例计算..."
cd $(dirname "$0")

# 如果有参数，尝试使用参数进行计算
if [ $# -gt 0 ]; then
    echo "使用传递的参数进行计算:"
    
    # 检查参数是否都是数字
    numbers=""
    for arg in "$@"; do
        if [[ $arg =~ ^-?[0-9]+(\.[0-9]+)?$ ]]; then
            numbers="$numbers $arg"
        else
            echo "警告: 参数 '$arg' 不是有效数字，将被忽略"
        fi
    done
    
    if [ -n "$numbers" ]; then
        python3 -c "
import sys
sys.path.append('../..')
from functions.calculator.main import main
import argparse

# 创建参数解析
args = argparse.Namespace()
args.numbers = [float(x) for x in '$numbers'.split()]
args.operation = 'add'
args.show_details = True

main(args)
"
    else
        echo "没有有效的数字参数，使用默认值"
        python3 -c "
import sys
sys.path.append('../..')
from functions.calculator.main import main
import argparse

args = argparse.Namespace()
args.numbers = [1, 2, 3, 4, 5]
args.operation = 'add'
args.show_details = True

main(args)
"
    fi
else
    python3 -c "
import sys
sys.path.append('../..')
from functions.calculator.main import main
import argparse

# 创建模拟参数
args = argparse.Namespace()
args.numbers = [1, 2, 3, 4, 5]
args.operation = 'add'
args.show_details = True

print('通过start.sh调用calculator模块:')
main(args)
"
fi

echo ""
echo "🎉 Calculator模块启动完成!"
echo "提示: 你也可以直接使用 'gtools calculator --help' 查看完整功能"