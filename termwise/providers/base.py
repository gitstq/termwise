"""
LLM Provider抽象基类

定义所有LLM Provider必须实现的统一接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseProvider(ABC):
    """LLM Provider抽象基类。

    所有LLM服务提供商必须继承此类并实现其抽象方法。
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化Provider。

        Args:
            config: Provider配置字典
        """
        self.config = config
        self.last_usage: Optional[Dict[str, int]] = None

    @abstractmethod
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
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，None则使用配置中的默认模型
            temperature: 采样温度
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Returns:
            模型生成的文本内容
        """
        raise NotImplementedError

    @abstractmethod
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
            tools: 可用工具列表（OpenAI function calling格式）
            model: 模型名称
            temperature: 采样温度
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Returns:
            包含content和tool_calls的字典
        """
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> List[Any]:
        """列出可用的模型。

        Returns:
            模型列表
        """
        raise NotImplementedError

    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型名称。

        Returns:
            默认模型名称
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider名称。"""
        raise NotImplementedError

    def get_usage(self) -> Optional[Dict[str, int]]:
        """获取上次请求的token使用量。

        Returns:
            包含prompt_tokens, completion_tokens, total_tokens的字典
        """
        return self.last_usage

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算API调用费用。

        Args:
            usage: token使用量字典

        Returns:
            估算费用（美元）
        """
        return 0.0
