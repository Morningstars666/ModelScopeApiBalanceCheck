"""
ModelScope余额查询FastAPI应用
使用异步HTTP请求查询ModelScope模型调用余量
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any, Optional
import asyncio

# 创建FastAPI应用
app = FastAPI(
    title="ModelScope余额查询API",
    description="查询ModelScope模型调用余量的API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelBalanceRequest(BaseModel):
    """查询余额请求模型"""
    models_: List[str]
    api_key: str


class ModelBalanceResponse(BaseModel):
    """模型余额响应模型"""
    model: str
    request_limit: Optional[int] = None
    request_remaining: Optional[int] = None
    model_request_limit: Optional[int] = None
    model_request_remaining: Optional[int] = None
    error: Optional[str] = None


class BatchBalanceResponse(BaseModel):
    """批量查询余额响应模型"""
    status: int = 0
    data: List[ModelBalanceResponse]
    msg: Optional[str] = None


async def query_model_balance(
    model_name: str,
    api_key: str,
    client: httpx.AsyncClient,
    max_retries: int = 2
) -> ModelBalanceResponse:
    """
    异步查询单个模型的余额信息
    
    Args:
        model_name: 模型名称
        api_key: API密钥
        client: httpx异步客户端
        max_retries: 最大重试次数
        
    Returns:
        ModelBalanceResponse: 模型余额信息
    """
    url = "https://api-inference.modelscope.cn/v1/chat/completions"
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 构建请求体
    data = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "回复一个字'好'"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 100,
        "enable_thinking": False
    }
    
    # 重试逻辑
    for attempt in range(max_retries + 1):
        try:
            # 发送异步请求
            response = await client.post(
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"请求响应: {response.content}")

            # 检查HTTP状态码
            response.raise_for_status()
            
            # 提取速率限制信息
            rate_limit_fields = [
                ("modelscope-ratelimit-requests-limit", "request_limit"),
                ("modelscope-ratelimit-requests-remaining", "request_remaining"),
                ("modelscope-ratelimit-model-requests-limit", "model_request_limit"),
                ("modelscope-ratelimit-model-requests-remaining", "model_request_remaining")
            ]
            
            balance_info = {
                "model": model_name,
                "request_limit": None,
                "request_remaining": None,
                "model_request_limit": None,
                "model_request_remaining": None,
                "error": None
            }
            
            for header_name, field_name in rate_limit_fields:
                header_value = response.headers.get(header_name)
                if header_value:
                    try:
                        balance_info[field_name] = int(header_value)
                    except ValueError:
                        balance_info[field_name] = header_value
            
            return ModelBalanceResponse(**balance_info)
            
        except httpx.HTTPStatusError as e:
            # 如果是429错误（速率限制），重试
            if e.response.status_code == 429 and attempt < max_retries:
                wait_time = (attempt + 1) * 2  # 递增等待时间
                import asyncio
                await asyncio.sleep(wait_time)
                continue
            
            error_msg = f"HTTP错误: {e.response.status_code}"
            return ModelBalanceResponse(
                model=model_name,
                error=error_msg
            )
        except httpx.RequestError as e:
            # 如果是网络错误，重试
            if attempt < max_retries:
                wait_time = (attempt + 1) * 2  # 递增等待时间
                import asyncio
                await asyncio.sleep(wait_time)
                continue
            
            error_msg = f"请求错误: {str(e)}"
            return ModelBalanceResponse(
                model=model_name,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            return ModelBalanceResponse(
                model=model_name,
                error=error_msg
            )
    
    # 如果所有重试都失败
    return ModelBalanceResponse(
        model=model_name,
        error="请求失败，请检查API密钥和模型名称是否正确"
    )


@app.post("/api/balance", response_model=BatchBalanceResponse)
async def query_balance(
    request: ModelBalanceRequest,
):
    """
    查询模型余额接口
    
    Args:
        request: 包含模型名称列表的请求体
        api_key: API密钥（从请求体中获取）
        
    Returns:
        BatchBalanceResponse: 批量查询结果
    """
    if not request.models_:
        raise HTTPException(status_code=400, detail="models列表不能为空")
    
    # 检查models列表中的元素是否为空字符串
    empty_models = [model for model in request.models_ if not model or not model.strip()]
    if empty_models:
        raise HTTPException(
            status_code=400, 
            detail=f"models列表中包含空字符串: {empty_models}"
        )
    
    # 检查api_key是否为空字符串
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(
            status_code=400, 
            detail="api_key不能为空"
        )
    
    # 使用异步客户端批量查询
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            query_model_balance(model_name, request.api_key, client)
            for model_name in request.models_
        ]
        results = await asyncio.gather(*tasks)
    
    return BatchBalanceResponse(
        data=results,
        msg=f"成功查询 {len(results)} 个模型的余额信息"
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    return content


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "ModelScope Balance Query"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)