#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "项目目录: $PROJECT_DIR"

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "警告: 建议在虚拟环境中安装"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 1
    fi
fi

echo "安装项目到当前Python环境..."
cd "$PROJECT_DIR"
pip install -e .

echo "验证安装..."
if command -v gtools >/dev/null 2>&1; then
    echo "✓ gtools 命令已成功安装"
    gtools list
else
    echo "✗ gtools 命令安装失败"
    echo "请检查 Python 环境的 bin 目录是否在 PATH 中"
    exit 1
fi

echo ""
echo "安装完成！"
echo ""
echo "使用示例："
echo "  gtools list                     # 列出所有模块"
echo "  gtools info module_name         # 查看模块信息"
echo "  gtools module_name -h           # 查看模块帮助"
echo "  gtools module_name --param val  # 运行模块"