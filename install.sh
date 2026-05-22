#!/bin/bash

set -e

echo "========================================"
echo "  电商价格对比工具 - 一键安装脚本"
echo "========================================"
echo ""

# 检测 Python 版本
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ 检测到 Python $PYTHON_VERSION"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 创建虚拟环境（可选）
if [ -d ".venv" ]; then
    echo "📦 发现已有虚拟环境 .venv"
    USE_VENV=1
elif [ "$1" = "--global" ]; then
    USE_VENV=0
else
    echo -n "是否创建虚拟环境？(推荐) [Y/n]: "
    read -r answer
    if [ "$answer" = "n" ] || [ "$answer" = "N" ]; then
        USE_VENV=0
    else
        USE_VENV=1
    fi
fi

if [ "$USE_VENV" = "1" ]; then
    if [ ! -d ".venv" ]; then
        echo "🔧 正在创建虚拟环境..."
        $PYTHON_CMD -m venv .venv
        echo "✅ 虚拟环境创建完成"
    fi

    echo "📦 激活虚拟环境..."
    source .venv/bin/activate
    PIP_CMD=".venv/bin/pip"
else
    PIP_CMD="pip3"
fi

# 安装依赖
echo "📦 安装依赖..."
$PIP_CMD install --upgrade pip -q
$PIP_CMD install flask -q

echo ""
echo "========================================"
echo "  ✅ 安装完成！"
echo "========================================"
echo ""
echo "使用方式："
echo ""
echo "  CLI 命令行工具："
if [ "$USE_VENV" = "1" ]; then
    echo "    source .venv/bin/activate"
    echo "    python -m price_compare.cli 手机"
    echo ""
    echo "  Web 演示页面："
    echo "    source .venv/bin/activate"
    echo "    python -m price_compare.server"
else
    echo "    python -m price_compare.cli 手机"
    echo ""
    echo "  Web 演示页面："
    echo "    python -m price_compare.server"
fi
echo ""
echo "  然后打开 http://localhost:5000"
echo ""
