"""
配置管理模块

负责加载、保存和管理Termwise的配置文件。
配置文件使用YAML格式，存储在用户主目录下的 ~/.termwise/config.yaml。
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG = {
    "default_provider": "openai",
    "providers": {
        "openai": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o",
        },
        "anthropic": {
            "api_key": "",
            "model": "claude-sonnet-4-20250514",
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "llama3",
        },
    },
    "settings": {
        "theme": "dark",
        "max_context_tokens": 128000,
        "auto_save": True,
        "cost_tracking": True,
    },
}


class ConfigManager:
    """配置管理器，负责配置文件的读写和管理。"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器。

        Args:
            config_path: 配置文件路径，默认为 ~/.termwise/config.yaml
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".termwise" / "config.yaml"
        self.config_dir = self.config_path.parent
        self._config: Dict[str, Any] = {}
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self) -> None:
        """确保配置目录存在。"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """从文件加载配置，如果文件不存在则使用默认配置。"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
            # 合并默认配置中缺失的字段
            self._config = self._merge_config(DEFAULT_CONFIG, self._config)
        else:
            self._config = DEFAULT_CONFIG.copy()
            self.save()
        return self._config

    def save(self) -> None:
        """将当前配置保存到文件。"""
        self._ensure_config_dir()
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def _merge_config(self, default: Dict, override: Dict) -> Dict:
        """递归合并配置字典，默认值为基础，override覆盖。"""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键。

        Args:
            key: 配置键，如 'providers.openai.model'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置值，支持点号分隔的嵌套键。

        Args:
            key: 配置键，如 'providers.openai.model'
            value: 要设置的值
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """获取指定Provider的配置。

        Args:
            provider_name: Provider名称

        Returns:
            Provider配置字典
        """
        return self.get(f"providers.{provider_name}", {})

    def get_default_provider(self) -> str:
        """获取默认Provider名称。"""
        return self.get("default_provider", "openai")

    def set_default_provider(self, provider_name: str) -> None:
        """设置默认Provider。

        Args:
            provider_name: Provider名称
        """
        self.set("default_provider", provider_name)
        self.save()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取设置项。

        Args:
            key: 设置键名
            default: 默认值

        Returns:
            设置值
        """
        return self.get(f"settings.{key}", default)

    def set_setting(self, key: str, value: Any) -> None:
        """设置设置项。

        Args:
            key: 设置键名
            value: 设置值
        """
        self.set(f"settings.{key}", value)
        self.save()

    @property
    def config(self) -> Dict[str, Any]:
        """返回完整配置字典的副本。"""
        return self._config.copy()

    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """列出所有已配置的Provider。"""
        return self.get("providers", {})

    def is_provider_configured(self, provider_name: str) -> bool:
        """检查Provider是否已配置（有API key或base_url）。

        Args:
            provider_name: Provider名称

        Returns:
            是否已配置
        """
        provider_config = self.get_provider_config(provider_name)
        if not provider_config:
            return False
        # Ollama只需要base_url
        if provider_name == "ollama":
            return bool(provider_config.get("base_url"))
        # 其他provider需要api_key
        return bool(provider_config.get("api_key"))
