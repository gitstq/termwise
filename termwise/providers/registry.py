"""
Provider注册表

管理所有可用的LLM Provider，支持动态注册和获取。
"""

from typing import Any, Dict, List, Optional, Type

from termwise.providers.base import BaseProvider
from termwise.providers.openai_provider import OpenAIProvider
from termwise.providers.anthropic_provider import AnthropicProvider
from termwise.providers.ollama_provider import OllamaProvider


class ProviderRegistry:
    """Provider注册表。

    管理Provider的注册、获取和列表功能。
    """

    # 内置Provider映射
    _BUILTIN_PROVIDERS: Dict[str, Type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    def __init__(self, config=None):
        """初始化Provider注册表。

        Args:
            config: ConfigManager实例或配置字典
        """
        self._providers: Dict[str, Type[BaseProvider]] = {}
        self._instances: Dict[str, BaseProvider] = {}
        self._config = config

        # 注册内置Provider
        for name, provider_cls in self._BUILTIN_PROVIDERS.items():
            self._providers[name] = provider_cls

    def register(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """注册一个新的Provider。

        Args:
            name: Provider名称
            provider_class: Provider类
        """
        self._providers[name] = provider_class

    def unregister(self, name: str) -> None:
        """取消注册一个Provider。

        Args:
            name: Provider名称
        """
        self._providers.pop(name, None)
        self._instances.pop(name, None)

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """获取指定名称的Provider实例。

        Args:
            name: Provider名称

        Returns:
            Provider实例，如果未找到则返回None
        """
        if name in self._instances:
            return self._instances[name]

        provider_class = self._providers.get(name)
        if not provider_class:
            return None

        # 获取Provider配置
        config = {}
        if self._config:
            if hasattr(self._config, "get_provider_config"):
                config = self._config.get_provider_config(name)
            elif isinstance(self._config, dict):
                config = self._config.get("providers", {}).get(name, {})

        try:
            instance = provider_class(config)
            self._instances[name] = instance
            return instance
        except Exception:
            return None

    def list_providers(self) -> List[str]:
        """列出所有已注册的Provider名称。

        Returns:
            Provider名称列表
        """
        return list(self._providers.keys())

    def get_provider_class(self, name: str) -> Optional[Type[BaseProvider]]:
        """获取指定名称的Provider类。

        Args:
            name: Provider名称

        Returns:
            Provider类，如果未找到则返回None
        """
        return self._providers.get(name)

    def create_provider(self, name: str, config: Dict[str, Any]) -> Optional[BaseProvider]:
        """使用指定配置创建Provider实例。

        Args:
            name: Provider名称
            config: Provider配置

        Returns:
            Provider实例
        """
        provider_class = self._providers.get(name)
        if not provider_class:
            return None
        return provider_class(config)

    def close_all(self) -> None:
        """关闭所有Provider实例。"""
        for instance in self._instances.values():
            if hasattr(instance, "close"):
                instance.close()
        self._instances.clear()
