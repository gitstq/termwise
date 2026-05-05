"""
Termwise - 终端AI编码助手

一个支持多LLM后端的终端AI编码助手，提供交互式TUI界面和命令行工具。
"""

__version__ = "0.1.0"
__author__ = "Termwise Team"
__description__ = "终端AI编码助手 - Terminal AI Coding Assistant"

from termwise.config import ConfigManager
from termwise.cli import cli

__all__ = ["__version__", "__author__", "__description__", "ConfigManager", "cli"]
