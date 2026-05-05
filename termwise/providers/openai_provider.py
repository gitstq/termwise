"""
OpenAI Provider

支持OpenAI API及兼容API（如DeepSeek、通义千问等）。
"""

import json
from typing import Any, Dict, List, Optional

import httpx

from termwise.providers.base import BaseProvider


# 模型价格表（美元/1000 tokens）
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "deepseek-chat": {"input": 0.00014, "output": 0.00028},
    "deepseek-coder": {"input": 0.00014, "output": 0.00028},
    "qwen-turbo": {"input": 0.0008, "output": 0.002},
    "qwen-plus": {"input": 0.004, "output": 0.012},
}


class OpenAIProvider(BaseProvider):
    """OpenAI API Provider。

    支持OpenAI官方API和兼容API（通过自定义base_url）。
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化OpenAI Provider。

        Args:
            config: 配置字典，需包含api_key，可选base_url和model
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        self.default_model = config.get("model", "gpt-4o")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    @property
    def name(self) -> str:
        """Provider名称。"""
        return "openai"

    def get_default_model(self) -> str:
        """获取默认模型名称。"""
        return self.default_model

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> str:
        """发送聊天补全请求。

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 采样温度
            max_tokens: 最大生成token数

        Returns:
            模型生成的文本内容
        """
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload.update(kwargs)

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        # 记录token使用量
        usage = data.get("usage", {})
        self.last_usage = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

        # 提取回复内容
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Dict[str, Any]:
        """发送带工具调用的聊天补全请求。

        Args:
            messages: 消息列表
            tools: 可用工具列表
            model: 模型名称
            temperature: 采样温度
            max_tokens: 最大生成token数

        Returns:
            包含content和tool_calls的字典
        """
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tool_choice": "auto",
        }
        payload.update(kwargs)

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        # 记录token使用量
        usage = data.get("usage", {})
        self.last_usage = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

        # 解析响应
        choices = data.get("choices", [])
        if not choices:
            return {"content": "", "tool_calls": []}

        message = choices[0].get("message", {})
        content = message.get("content", "")
        raw_tool_calls = message.get("tool_calls", [])

        # 解析工具调用
        tool_calls = []
        for tc in raw_tool_calls:
            tool_calls.append({
                "id": tc.get("id", ""),
                "name": tc.get("function", {}).get("name", ""),
                "arguments": tc.get("function", {}).get("arguments", "{}"),
            })

        return {"content": content, "tool_calls": tool_calls}

    def list_models(self) -> List[Any]:
        """列出可用的模型。"""
        try:
            response = self._client.get("/models")
            response.raise_for_status()
            data = response.json()
            models = data.get("data", [])
            # 按ID排序
            models.sort(key=lambda x: x.get("id", ""))
            return models
        except Exception:
            # 如果API调用失败，返回已知模型列表
            return [
                {"id": "gpt-4o", "description": "GPT-4o 多模态模型"},
                {"id": "gpt-4o-mini", "description": "GPT-4o mini 轻量模型"},
                {"id": "gpt-4-turbo", "description": "GPT-4 Turbo"},
                {"id": "gpt-3.5-turbo", "description": "GPT-3.5 Turbo"},
            ]

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算API调用费用。

        Args:
            usage: token使用量字典

        Returns:
            估算费用（美元）
        """
        pricing = MODEL_PRICING.get(self.default_model, {"input": 0.01, "output": 0.03})
        input_cost = usage.get("prompt_tokens", 0) / 1000 * pricing["input"]
        output_cost = usage.get("completion_tokens", 0) / 1000 * pricing["output"]
        return input_cost + output_cost

    def close(self) -> None:
        """关闭HTTP客户端。"""
        self._client.close()
