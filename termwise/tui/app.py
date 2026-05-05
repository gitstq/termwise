"""Main TUI application for TermWise."""

from __future__ import annotations

import asyncio
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Label, Static, TabbedContent, TabPane

from termwise.agent.core import AgentCore
from termwise.agent.planner import TaskPlanner
from termwise.config import ConfigManager
from termwise.tui.themes import THEMES, get_theme
from termwise.tui.widgets import (
    ChatLog,
    CodePreview,
    InputArea,
    MessageBubble,
    PlanView,
    StatusBar,
)
from termwise.utils.cost_tracker import CostTracker
from termwise.utils.token_counter import TokenCounter


class TermWiseApp(App):
    """The main TermWise TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
    }

    #chat-panel {
        width: 2fr;
        padding: 1;
    }

    #side-panel {
        width: 1fr;
        padding: 1;
        border-left: solid $primary;
    }

    #input-container {
        height: auto;
        max-height: 6;
        padding: 1;
        border-top: solid $primary;
    }

    #status-bar {
        height: 1;
        dock: bottom;
    }

    .input-label {
        color: $text;
        margin-bottom: 0;
    }

    #chat-input {
        margin-bottom: 0;
    }

    ChatLog {
        height: 1fr;
    }

    PlanView {
        height: auto;
        max-height: 40%;
        margin-bottom: 1;
    }

    CodePreview {
        height: 1fr;
    }

    MessageBubble {
        margin-bottom: 1;
    }
    """

    TITLE = "TermWise"
    SUB_TITLE = "Terminal AI Coding Assistant"

    BINDINGS = [
        Binding("ctrl+n", "new_conversation", "New Chat"),
        Binding("ctrl+t", "toggle_theme", "Toggle Theme"),
        Binding("ctrl+c", "cancel_generation", "Cancel"),
        Binding("ctrl+l", "clear_screen", "Clear"),
        Binding("ctrl+p", "toggle_plan", "Toggle Plan"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, config_manager: Optional[ConfigManager] = None, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = config_manager or ConfigManager()
        self.agent: Optional[AgentCore] = None
        self.cost_tracker = CostTracker()
        self.token_counter = TokenCounter()
        self._current_theme_name = self.config_manager.get("settings", "theme") or "dark"
        self._is_generating = False
        self._cancel_event = asyncio.Event()
        self._conversation_history: list[dict] = []

    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header(show_clock=True)

        with Container(id="main-container"):
            with Vertical(id="chat-panel"):
                yield ChatLog(id="chat-log")
            with Vertical(id="side-panel"):
                yield PlanView(id="plan-view")
                yield CodePreview(id="code-preview")

        with Container(id="input-container"):
            yield InputArea(id="input-area")

        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        theme = get_theme(self._current_theme_name)
        self.theme = theme.name if hasattr(theme, "name") else "termwise_dark"
        for theme_obj in THEMES.values():
            self.register_theme(theme_obj)

        self._update_status_bar()
        self._initialize_agent()

        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_message(
            "system",
            "Welcome to **TermWise** — your terminal AI coding assistant! 🚀\n\n"
            "Type your coding question or task below. I can read files, write code, "
            "execute commands, and help you build software.\n\n"
            "**Shortcuts:** `Ctrl+N` New Chat | `Ctrl+T` Theme | `Ctrl+P` Plan | `Ctrl+C` Cancel",
        )

    def _initialize_agent(self) -> None:
        """Initialize the AI agent with configured provider."""
        try:
            from termwise.providers.registry import ProviderRegistry
            from termwise.tools.file_reader import FileReaderTool
            from termwise.tools.file_writer import FileWriterTool
            from termwise.tools.shell import ShellTool
            from termwise.tools.search import SearchTool

            registry = ProviderRegistry(self.config_manager)
            provider_name = self.config_manager.get_default_provider()
            provider = registry.get_provider(provider_name)

            tools = [FileReaderTool(), FileWriterTool(), ShellTool(), SearchTool()]

            if provider:
                self.agent = AgentCore(
                    provider=provider,
                    tools=tools,
                    cost_tracker=self.cost_tracker,
                )
                model = self.config_manager.get("providers", provider_name, "model")
                if model:
                    self.query_one("#status-bar", StatusBar).model = model
        except Exception as e:
            chat_log = self.query_one("#chat-log", ChatLog)
            chat_log.add_message(
                "system",
                f"⚠️ Agent initialization warning: {e}\n\n"
                "You can still use TermWise, but AI features require proper configuration.\n"
                "Run `termwise config` to set up your API keys.",
            )

    def on_input_area_submitted(self, message: InputArea.Submitted) -> None:
        """Handle user input submission."""
        if self._is_generating:
            return
        self._handle_user_message(message.text)

    @work(exclusive=True)
    async def _handle_user_message(self, text: str) -> None:
        """Process a user message."""
        self._is_generating = True
        self._cancel_event.clear()
        self.query_one("#status-bar", StatusBar).is_generating = True

        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_message("user", text)

        self._conversation_history.append({"role": "user", "content": text})

        bubble = chat_log.add_streaming_message("assistant")
        full_response = ""

        try:
            if self.agent:
                response = await self.agent.chat(text)
                full_response = response
                bubble.content = full_response or "No response received."
                self._conversation_history.append({"role": "assistant", "content": full_response})

                tokens = self.token_counter.count_messages(self._conversation_history)
                self.query_one("#status-bar", StatusBar).tokens_used = tokens

                provider_name = self.config_manager.get("default_provider", "unknown")
                cost = self.cost_tracker.get_total_cost()
                self.query_one("#status-bar", StatusBar).total_cost = cost

                self._extract_and_show_code(full_response)
            else:
                bubble.content = "⚠️ No AI agent configured. Run `termwise config` to set up API keys."

        except asyncio.CancelledError:
            bubble.content = full_response + "\n\n_⏹️ Generation cancelled_"
        except Exception as e:
            bubble.content = f"❌ Error: {e}"
        finally:
            self._is_generating = False
            self.query_one("#status-bar", StatusBar).is_generating = False

    def _extract_and_show_code(self, text: str) -> None:
        """Extract code blocks from response and show in preview."""
        import re

        code_blocks = re.findall(r"```(\w+)?\n(.*?)```", text, re.DOTALL)
        if code_blocks:
            lang, code = code_blocks[-1]
            preview = self.query_one("#code-preview", CodePreview)
            preview.set_code(code.strip(), lang or "text")

    def action_new_conversation(self) -> None:
        """Start a new conversation."""
        if self._is_generating:
            self._cancel_event.set()
        self._conversation_history.clear()
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.clear()
        chat_log.add_message("system", "🔄 New conversation started.")
        plan_view = self.query_one("#plan-view", PlanView)
        plan_view.set_plan("")
        code_preview = self.query_one("#code-preview", CodePreview)
        code_preview.set_code("", "python")

    def action_toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        self._current_theme_name = "light" if self._current_theme_name == "dark" else "dark"
        theme = get_theme(self._current_theme_name)
        self.theme = theme.name if hasattr(theme, "name") else "termwise_dark"
        self.config_manager.set("settings", "theme", self._current_theme_name)
        self.config_manager.save()

    def action_cancel_generation(self) -> None:
        """Cancel the current generation."""
        if self._is_generating:
            self._cancel_event.set()

    def action_clear_screen(self) -> None:
        """Clear the chat log."""
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.clear()

    def action_toggle_plan(self) -> None:
        """Toggle plan visibility."""
        plan_view = self.query_one("#plan-view", PlanView)
        plan_view.set_display(not plan_view.display)

    def _update_status_bar(self) -> None:
        """Update the status bar with current info."""
        status_bar = self.query_one("#status-bar", StatusBar)
        provider = self.config_manager.get("default_provider", "N/A")
        model = self.config_manager.get("providers", provider, "model", "N/A")
        status_bar.model = f"{provider}/{model}"
        status_bar.total_cost = self.cost_tracker.get_total_cost()
