#!/bin/bash

# ModelScope余额查询项目部署脚本
# 功能：安装依赖并启动FastAPI服务

set -e  # 遇到错误立即退出

echo "=========================================="
echo "ModelScope余额查询项目部署脚本"
echo "=========================================="
echo ""

# 检查Python是否安装
echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python版本: $PYTHON_VERSION"
echo ""

# 检查requirements.txt是否存在
echo "2. 检查依赖文件..."
if [ ! -f "requirements.txt" ]; then
    echo "错误：未找到requirements.txt文件"
    exit 1
fi
echo "✓ 找到requirements.txt"
echo ""

# 安装依赖
echo "3. 安装项目依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ 依赖安装完成"
echo ""

# 启动服务
echo "4. 启动FastAPI服务..."
echo ""
echo "=========================================="
echo "服务已启动！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  - API文档: http://localhost:8000/docs"
echo "  - 健康检查: http://localhost:8000/health"
echo "  - 前端页面: http://localhost:8000/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 运行uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000