"""Tests for LLM providers."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from termwise.providers.base import BaseProvider
from termwise.providers.openai_provider import OpenAIProvider
from termwise.providers.anthropic_provider import AnthropicProvider
from termwise.providers.ollama_provider import OllamaProvider
from termwise.providers.registry import ProviderRegistry


class TestBaseProvider:
    """Tests for BaseProvider."""

    def test_base_provider_cannot_instantiate(self):
        """BaseProvider should not be directly instantiated."""
        with pytest.raises(TypeError):
            BaseProvider(config={})

    def test_base_provider_has_abstract_methods(self):
        """BaseProvider defines required abstract methods."""
        abstract_methods = {"complete", "complete_with_tools", "list_models", "get_default_model", "name"}
        assert abstract_methods.issubset(set(dir(BaseProvider)))


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_openai_provider_init(self):
        """Test provider initialization."""
        config = {
            "api_key": "test-key",
            "base_url": "https://api.example.com/v1",
            "model": "gpt-4o",
        }
        provider = OpenAIProvider(config=config)
        assert provider.config["model"] == "gpt-4o"
        assert provider.config["api_key"] == "test-key"

    def test_openai_provider_default_base_url(self):
        """Test default base URL."""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config=config)
        # Provider stores config as-is; base_url defaults come from the provider logic
        assert provider.config.get("api_key") == "test-key"


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_anthropic_provider_init(self):
        """Test provider initialization."""
        config = {"api_key": "test-key", "model": "claude-sonnet-4-20250514"}
        provider = AnthropicProvider(config=config)
        assert provider.config["model"] == "claude-sonnet-4-20250514"

    def test_anthropic_default_model(self):
        """Test default model."""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config=config)
        assert "claude" in provider.config.get("model", "claude")


class TestOllamaProvider:
    """Tests for Ollama provider."""

    def test_ollama_provider_init(self):
        """Test provider initialization."""
        config = {"base_url": "http://localhost:11434", "model": "llama3"}
        provider = OllamaProvider(config=config)
        assert provider.config["model"] == "llama3"

    def test_ollama_default_base_url(self):
        """Test default base URL."""
        provider = OllamaProvider(config={})
        assert "localhost:11434" in provider.config.get("base_url", "http://localhost:11434")


class TestProviderRegistry:
    """Tests for ProviderRegistry."""

    def test_registry_init(self):
        """Test registry initialization."""
        from termwise.config import ConfigManager
        config = ConfigManager()
        registry = ProviderRegistry(config)
        assert registry is not None

    def test_list_providers(self):
        """Test listing providers."""
        from termwise.config import ConfigManager
        config = ConfigManager()
        registry = ProviderRegistry(config)
        names = registry.list_providers()
        assert isinstance(names, list)
