"""
Anthropic Provider

支持Anthropic Claude系列模型。
"""

import json
from typing import Any, Dict, List, Optional

import httpx

from termwise.providers.base import BaseProvider


# Claude模型价格表（美元/1000 tokens）
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-opus-4-20250514": {"input": 0.015, "output": 0.075},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
}


class AnthropicProvider(BaseProvider):
    """Anthropic Claude Provider。

    支持Claude系列模型的API调用。
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化Anthropic Provider。

        Args:
            config: 配置字典，需包含api_key，可选model
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get(
            "base_url", "https://api.anthropic.com"
        ).rstrip("/")
        self.default_model = config.get("model", "claude-sonnet-4-20250514")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    @property
    def name(self) -> str:
        """Provider名称。"""
        return "anthropic"

    def get_default_model(self) -> str:
        """获取默认模型名称。"""
        return self.default_model

    def _convert_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """将OpenAI格式的消息转换为Anthropic格式。

        Anthropic API要求system消息单独传递，且消息必须交替user/assistant。

        Args:
            messages: OpenAI格式的消息列表

        Returns:
            (system_prompt, anthropic_messages) 元组
        """
        system_prompt = ""
        anthropic_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_prompt = content
            elif role == "tool":
                # 工具结果消息转换为user消息
                anthropic_messages.append({
                    "role": "user",
                    "content": content,
                })
            else:
                anthropic_messages.append({
                    "role": role,
                    "content": content,
                })

        return system_prompt, anthropic_messages

    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将OpenAI格式的工具定义转换为Anthropic格式。

        Args:
            tools: OpenAI function calling格式的工具列表

        Returns:
            Anthropic格式的工具列表
        """
        anthropic_tools = []
        for tool in tools:
            func = tool.get("function", {})
            anthropic_tools.append({
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {"type": "object", "properties": {}}),
            })
        return anthropic_tools

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
        system_prompt, anthropic_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_prompt:
            payload["system"] = system_prompt
        payload.update(kwargs)

        response = self._client.post("/v1/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        # 记录token使用量
        usage = data.get("usage", {})
        self.last_usage = {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        }

        # 提取回复内容
        content_blocks = data.get("content", [])
        text_parts = []
        for block in content_blocks:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts)

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
        system_prompt, anthropic_messages = self._convert_messages(messages)
        anthropic_tools = self._convert_tools(tools)

        payload: Dict[str, Any] = {
            "model": model,
            "messages": anthropic_messages,
            "tools": anthropic_tools,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_prompt:
            payload["system"] = system_prompt
        payload.update(kwargs)

        response = self._client.post("/v1/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        # 记录token使用量
        usage = data.get("usage", {})
        self.last_usage = {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        }

        # 解析响应
        content_blocks = data.get("content", [])
        text_parts = []
        tool_calls = []

        for block in content_blocks:
            block_type = block.get("type", "")
            if block_type == "text":
                text_parts.append(block.get("text", ""))
            elif block_type == "tool_use":
                tool_calls.append({
                    "id": block.get("id", ""),
                    "name": block.get("name", ""),
                    "arguments": json.dumps(block.get("input", {})),
                })

        return {"content": "\n".join(text_parts), "tool_calls": tool_calls}

    def list_models(self) -> List[Any]:
        """列出可用的模型。"""
        # Anthropic没有公开的模型列表API，返回已知模型
        return [
            {"id": "claude-opus-4-20250514", "description": "Claude Opus 4 - 最强大模型"},
            {"id": "claude-sonnet-4-20250514", "description": "Claude Sonnet 4 - 平衡性能"},
            {"id": "claude-3-5-sonnet-20241022", "description": "Claude 3.5 Sonnet"},
            {"id": "claude-3-5-haiku-20241022", "description": "Claude 3.5 Haiku - 快速轻量"},
            {"id": "claude-3-opus-20240229", "description": "Claude 3 Opus"},
            {"id": "claude-3-sonnet-20240229", "description": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku-20240307", "description": "Claude 3 Haiku"},
        ]

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算API调用费用。

        Args:
            usage: token使用量字典

        Returns:
            估算费用（美元）
        """
        pricing = MODEL_PRICING.get(
            self.default_model, {"input": 0.003, "output": 0.015}
        )
        input_cost = usage.get("prompt_tokens", 0) / 1000 * pricing["input"]
        output_cost = usage.get("completion_tokens", 0) / 1000 * pricing["output"]
        return input_cost + output_cost

    def close(self) -> None:
        """关闭HTTP客户端。"""
        self._client.close()
