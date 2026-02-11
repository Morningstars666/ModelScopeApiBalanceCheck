#!/bin/bash

# ModelScope余额查询项目部署脚本
# 功能：使用uv安装依赖并启动FastAPI服务

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

# 检查uv是否安装
echo "2. 检查uv包管理器..."
if ! command -v uv &> /dev/null; then
    echo "警告：未找到uv，将自动安装..."
    echo "正在执行安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        echo "✓ uv 安装成功"
        export PATH="$HOME/.local/bin:$PATH"
        USE_UV=true
    else
        echo "✗ uv 安装失败，将回退到pip方式"
        USE_UV=false
    fi
else
    echo "✓ 找到uv"
    USE_UV=true
fi
echo ""

# 检查pyproject.toml是否存在
echo "3. 检查依赖配置文件..."
if [ ! -f "pyproject.toml" ]; then
    echo "错误：未找到pyproject.toml文件"
    exit 1
fi
echo "✓ 找到pyproject.toml"
echo ""

# 安装依赖
echo "4. 安装项目依赖..."
if [ "$USE_UV" = true ]; then
    uv sync --no-dev
    echo "✓ 依赖安装完成 (使用uv)"
else
    # 回退到pip方式
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
        echo "✓ 依赖安装完成 (使用pip)"
    else
        echo "错误：既没有uv也没有requirements.txt"
        exit 1
    fi
fi
echo ""

# 启动服务
echo "5. 启动FastAPI服务..."
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

# 运行服务
if [ "$USE_UV" = true ]; then
    uv run uvicorn main:app --host 0.0.0.0 --port 8000
else
    uvicorn main:app --host 0.0.0.0 --port 8000
fi