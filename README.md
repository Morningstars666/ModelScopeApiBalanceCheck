# ModelScope API 余额查询工具

一个用于查询 ModelScope API 额度的轻量级 Web 应用，支持批量查询多个模型的请求限制和剩余额度。

## 项目简介

本项目提供了一个 Web 界面，可以快速查询 ModelScope API Key 的额度使用情况。通过调用 ModelScope 的 chat completions 接口，从响应头中提取额度信息，并展示出来。
读取的响应头如下，源自[https://modelscope.cn/docs/model-service/API-Inference/limits](https://modelscope.cn/docs/model-service/API-Inference/limits)
| 响应头 | 描述 | 示例值 |
| --- | --- | --- |
| modelscope-ratelimit-requests-limit | 用户当天限额 | 2000 |
| modelscope-ratelimit-requests-remaining | 用户当天剩余额度 | 500 |
| modelscope-ratelimit-model-requests-limit | 模型当天限额 | 500 |
| modelscope-ratelimit-model-requests-remaining | 模型当天剩余额度 | 20 |

**在线演示**: [checkapi.qciy.site](http://checkapi.qciy.site)

## 技术栈

- **编程语言**: Go 1.26.0
- **后端框架**: [Fiber](https://gofiber.io) v3 - 基于 Fasthttp 的高性能 Go Web 框架
- **HTTP 客户端**: 标准库 `net/http`

## 实现思路

1. **前端界面** (`index.html`)
   - 提供简洁的表单输入，支持批量输入多个模型名称
   - 实时展示查询结果，包括：
     - 模型名称
     - 请求限制 (Request Limit)
     - 剩余请求数 (Request Remaining)
     - 模型级限制 (Model Request Limit)
     - 模型级剩余 (Model Request Remaining)
     - 错误信息（如查询失败）

2. **后端 API** (`main.go`, `handler.go`)
   - `GET /` - 返回前端页面
   - `GET /health` - 健康检查接口
   - `POST /api/balance` - 核心查询接口

3. **额度查询流程**
   - 接收前端传来的 `models` 数组和 `api_key`
   - 对每个模型并发发送请求到 ModelScope API
   - 从响应头中解析额度信息：
     - `modelscope-ratelimit-requests-limit`
     - `modelscope-ratelimit-requests-remaining`
     - `modelscope-ratelimit-model-requests-limit`
     - `modelscope-ratelimit-model-requests-remaining`
   - 返回结构化的查询结果

## 部署说明

### 前置要求

- Go 1.26.0 或更高版本

### 本地运行

1. 克隆或下载项目代码

2. 安装依赖：
   ```bash
   go mod download
   ```

3. 启动服务：
   ```bash
   go run main.go handler.go
   ```

4. 访问应用：
   - 打开浏览器访问 `http://localhost:3000`
   - 健康检查：`http://localhost:3000/health`

### 生产环境部署

#### 使用系统服务（以 Linux 为例）

1. 编译二进制文件：
   ```bash
   go build -o modelscope-balance main.go handler.go
   ```

2. 创建 systemd 服务文件 `/etc/systemd/system/modelscope-balance.service`：
   ```ini
   [Unit]
   Description=ModelScope Balance Check Service
   After=network.target

   [Service]
   Type=simple
   User=youruser
   WorkingDirectory=/path/to/project
   ExecStart=/path/to/project/modelscope-balance
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. 启动服务：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable modelscope-balance
   sudo systemctl start modelscope-balance
   ```

#### 使用 Docker

创建 `Dockerfile`：
```dockerfile
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o modelscope-balance main.go handler.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/modelscope-balance .
COPY --from=builder /app/index.html .
EXPOSE 3000
CMD ["./modelscope-balance"]
```

构建并运行：
```bash
docker build -t modelscope-balance .
docker run -d -p 3000:3000 modelscope-balance
```

#### 使用反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name checkapi.qciy.site;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 项目结构

```
ModelScopeApiBalanceCheck/
├── main.go          # 应用入口，路由配置
├── handler.go       # 业务逻辑处理
├── index.html       # 前端页面
├── go.mod           # Go 依赖管理
├── go.sum           # 依赖校验
└── README.md        # 项目说明
```

## API 文档

### 查询余额

**请求**:
- 方法: POST
- 路径: `/api/balance`
- Content-Type: `application/json`

**请求体**:
```json
{
  "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-R1"],
  "api_key": "your-api-key-here"
}
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "model": "Qwen/Qwen2.5-7B-Instruct",
      "request_limit": 100,
      "request_remaining": 95,
      "model_request_limit": 100,
      "model_request_remaining": 95,
      "error": null
    }
  ],
  "message": "成功查询 1 个模型的余额信息"
}
```

### 健康检查

**请求**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "service": "ModelScope Balance Query"
}
```

## 注意事项

- 本项目仅用于查询额度，不会保存任何 API Key 或查询记录
- 由于前端限制访问自定义的请求头，所有查询均在服务器端直接转发到 ModelScope API
- 请勿将 API Key 泄露给他人

***本文档由AI生成，请自行verfy***