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
├── requirements.txt     # 项目依赖
└── README.md           # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python main.py
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

- `fastapi>=0.104.1`: Web框架
- `uvicorn[standard]>=0.24.0`: ASGI服务器
- `httpx>=0.25.0`: 异步HTTP客户端
- `pydantic>=2.5.0`: 数据验证

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
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产部署

使用gunicorn + uvicorn workers：

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署

创建Dockerfile：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t modelscope-balance-query .
docker run -p 8000:8000 modelscope-balance-query
```

## 许可证

本项目仅供学习和参考使用。

## 免责声明
README.md文档由AI生成，请自行verify。