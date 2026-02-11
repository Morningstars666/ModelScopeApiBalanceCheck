# ModelScope余额查询FastAPI应用

这是一个基于FastAPI的ModelScope模型调用余量查询服务，支持异步请求和Web界面。

可使用以下链接直接使用项目：[ModelScope API 余量查询](https://checkapi.qciy.site/)

## 功能特性

- ✅ 使用FastAPI框架构建
- ✅ 完全异步请求处理
- ✅ 支持批量查询多个模型余额
- ✅ 提供Web界面（使用amis框架）
- ✅ 完整的异常处理机制
- ✅ API Key通过请求头传递
- ✅ CORS跨域支持

## 项目结构

```
检查ModelScope余额/
├── main.py              # FastAPI主应用
├── pyproject.toml       # 项目依赖配置 (uv)
├── uv.lock              # 依赖锁文件
├── requirements.txt     # 旧版依赖文件（保留用于参考）
└── README.md           # 项目说明
```

## 快速开始

### 1. 安装依赖 (使用 uv)

本项目已迁移至 [uv](https://github.com/astral-sh/uv) 包管理器，推荐使用以下命令：

```bash
# 同步安装所有依赖（包括开发依赖）
uv sync

# 仅安装生产依赖
uv sync --no-dev

# 或使用 pip 安装（如果需要）
uv pip install -r requirements.txt
```

### 2. 运行服务

使用以下命令启动服务：

```bash
uv run python main.py
```

或直接使用 uvicorn：

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

### 3. 访问Web界面

在浏览器中打开 `http://localhost:8000`，即可使用Web界面查询模型余额。

## API接口

### 查询余额接口

**接口地址**: `POST /api/balance`

**请求体**:
```json
{
  "models": ["Qwen/Qwen3-Coder-480B-A35B-Instruct", "ZhipuAI/GLM-4.7"]
  "api_key": "your-api-key"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
      "request_limit": 100,
      "request_remaining": 95,
      "model_request_limit": 50,
      "model_request_remaining": 48,
      "error": null
    },
    {
      "model": "ZhipuAI/GLM-4.7",
      "request_limit": 100,
      "request_remaining": 95,
      "model_request_limit": 50,
      "model_request_remaining": 48,
      "error": null
    }
  ],
  "message": "成功查询 2 个模型的余额信息"
}
```

### 健康检查接口

**接口地址**: `GET /health`

**响应示例**:
```json
{
  "status": "healthy",
  "service": "ModelScope Balance Query"
}
```

## Web界面使用说明

1. **输入API Key**: 在页面顶部输入您的ModelScope API Key
2. **输入模型列表**: 在页面顶部输入要查询的模型名称，多个模型用逗号分隔
3. **点击查询**: 点击"查询"按钮开始查询
4. **查看结果**: 查询结果会以表格形式显示，包含以下信息：
   - 模型名称
   - 请求限制
   - 请求剩余
   - 模型请求限制
   - 模型请求剩余

## 技术栈

- **FastAPI**: 现代化的Python Web框架
- **httpx**: 异步HTTP客户端
- **amis**: 百度开源的前端低代码框架
- **Pydantic**: 数据验证和设置管理
- **uv**: 极速Python包管理器和解析器

## 核心功能

### 异步查询

使用`httpx.AsyncClient`进行异步HTTP请求，支持并发查询多个模型。

### 速率限制提取

自动从ModelScope API响应头中提取以下4个关键速率限制字段：

1. `modelscope-ratelimit-requests-limit`: 总请求限制
2. `modelscope-ratelimit-requests-remaining`: 剩余请求次数
3. `modelscope-ratelimit-model-requests-limit`: 单模型请求限制
4. `modelscope-ratelimit-model-requests-remaining`: 单模型剩余请求次数

### 错误处理

完整的异常处理机制：

- HTTP状态错误
- 网络请求错误
- JSON解析错误
- 其他未知错误

## 配置说明

### 依赖版本

- `fastapi>=0.128.7`: Web框架
- `uvicorn>=0.40.0`: ASGI服务器
- `httpx>=0.28.1`: 异步HTTP客户端

依赖版本在 `pyproject.toml` 中管理。

### 超时设置

默认超时时间为30秒，可在`main.py`中修改`timeout`参数。

## 使用示例

### Python客户端示例

```python
import httpx

# 查询单个模型
async def query_balance():
    async with httpx.AsyncClient() as client:
        headers = {
            "X-API-Key": "your_api_key_here",
            "Content-Type": "application/json"
        }
        data = {
            "models": ["Qwen/Qwen3-Coder-480B-A35B-Instruct"]
        }
        response = await client.post(
            "http://localhost:8000/api/balance",
            headers=headers,
            json=data
        )
        print(response.json())

# 并发查询多个模型
async def query_multiple_models():
    async with httpx.AsyncClient() as client:
        headers = {
            "X-API-Key": "your_api_key_here",
            "Content-Type": "application/json"
        }
        data = {
            "models": [
                "Qwen/Qwen3-Coder-480B-A35B-Instruct",
                "ZhipuAI/GLM-4.7",
                "Qwen/Qwen2.5-72B-Instruct"
            ]
        }
        response = await client.post(
            "http://localhost:8000/api/balance",
            headers=headers,
            json=data
        )
        print(response.json())

# 运行示例
query_balance()
query_multiple_models()
```

## 注意事项

1. 请确保您有有效的ModelScope API密钥
2. 注意API的速率限制，避免频繁调用
3. 根据实际情况调整超时时间（当前设置为30秒）
4. 如果遇到网络问题，程序会显示详细的错误信息
5. API Key通过请求头传递，请妥善保管

## 开发与部署

### 开发模式

使用uvicorn开发模式运行：

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或使用部署脚本：

```bash
bash deploy.sh
```

### 生产部署

使用gunicorn + uvicorn workers：

```bash
uv pip install gunicorn
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署

创建Dockerfile：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY main.py .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t modelscope-balance-query .
docker run -p 8000:8000 modelscope-balance-query
```

## 关于 uv

[uv](https://github.com/astral-sh/uv) 是一个极快的 Python 包管理器和解析器，相比传统的 pip：

- 🚀 **极速安装**: 使用 Rust 编写，并行操作，速度显著提升
- 📦 **现代化的依赖解析**: 基于 `pyproject.toml` 标准
- 🔒 **锁文件支持**: `uv.lock` 确保依赖版本一致性
- 🎯 **完美兼容**: 完全兼容 pip 和 requirements.txt

常用命令：

```bash
# 添加新依赖
uv add fastapi

# 更新依赖
uv sync

# 升级所有依赖到最新版本
uv pip compile -U pyproject.toml -o uv.lock

# 查看已安装的包
uv pip list
```

## 许可证

本项目仅供学习和参考使用。

## 免责声明

README.md文档由AI生成，请自行verify。