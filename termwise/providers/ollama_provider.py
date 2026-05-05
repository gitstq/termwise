"""
Ollama Provider

支持本地Ollama模型服务。
"""

import json
from typing import Any, Dict, List, Optional

import httpx

from termwise.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama本地模型 Provider。

    通过Ollama REST API与本地运行的模型交互。
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化Ollama Provider。

        Args:
            config: 配置字典，需包含base_url，可选model
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434").rstrip("/")
        self.default_model = config.get("model", "llama3")
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=300.0,  # 本地模型可能需要更长时间
        )

    @property
    def name(self) -> str:
        """Provider名称。"""
        return "ollama"

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
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

        # 记录token使用量（Ollama的token计数可能不精确）
        eval_count = data.get("eval_count", 0)
        prompt_eval_count = data.get("prompt_eval_count", 0)
        self.last_usage = {
            "prompt_tokens": prompt_eval_count,
            "completion_tokens": eval_count,
            "total_tokens": prompt_eval_count + eval_count,
        }

        return data.get("message", {}).get("content", "")

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

        Ollama对工具调用的支持有限，这里使用简单的文本解析方式。

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

        # 构建工具描述，添加到系统消息中
        tool_descriptions = "\n\n可用工具:\n"
        for tool in tools:
            func = tool.get("function", {})
            tool_descriptions += f"- {func.get('name', '')}: {func.get('description', '')}\n"
            params = func.get("parameters", {}).get("properties", {})
            if params:
                tool_descriptions += "  参数:\n"
                for param_name, param_info in params.items():
                    tool_descriptions += f"    - {param_name}: {param_info.get('description', '')}\n"

        # 在消息前面添加工具描述
        augmented_messages = messages.copy()
        if augmented_messages and augmented_messages[0].get("role") == "system":
            augmented_messages[0]["content"] += tool_descriptions
        else:
            augmented_messages.insert(0, {
                "role": "system",
                "content": f"你是一个AI助手，可以使用以下工具来帮助用户。当你需要使用工具时，请使用以下JSON格式回复:\n"
                           f"{{{{\"tool\": \"工具名\", \"arguments\": {{}}}}}}\n{tool_descriptions}",
            })

        content = self.complete(
            messages=augmented_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 尝试解析工具调用
        tool_calls = self._parse_tool_calls(content)
        if tool_calls:
            # 如果解析到工具调用，从content中移除工具调用部分
            clean_content = content
            for tc in tool_calls:
                clean_content = clean_content.replace(
                    json.dumps({"tool": tc["name"], "arguments": json.loads(tc["arguments"])}),
                    ""
                ).strip()
            return {"content": clean_content, "tool_calls": tool_calls}

        return {"content": content, "tool_calls": []}

    def _parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """从文本内容中解析工具调用。

        Args:
            content: 模型生成的文本

        Returns:
            工具调用列表
        """
        tool_calls = []
        # 尝试找到JSON格式的工具调用
        try:
            # 查找可能的JSON块
            import re
            json_pattern = r'\{[\s\S]*?"tool"[\s\S]*?"arguments"[\s\S]*?\}'
            matches = re.findall(json_pattern, content)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if "tool" in parsed and "arguments" in parsed:
                        tool_calls.append({
                            "id": f"call_{len(tool_calls)}",
                            "name": parsed["tool"],
                            "arguments": json.dumps(parsed["arguments"]),
                        })
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass
        return tool_calls

    def list_models(self) -> List[Any]:
        """列出本地可用的Ollama模型。"""
        try:
            response = self._client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            models = []
            for model in data.get("models", []):
                model_name = model.get("name", "")
                size = model.get("size", 0)
                size_gb = size / (1024 ** 3) if size else 0
                models.append({
                    "id": model_name,
                    "description": f"{size_gb:.1f} GB",
                })
            return models
        except Exception:
            return [{"id": self.default_model, "description": "默认模型"}]

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算费用（本地模型免费）。

        Args:
            usage: token使用量字典

        Returns:
            始终返回0.0
        """
        return 0.0

    def close(self) -> None:
        """关闭HTTP客户端。"""
        self._client.close()
