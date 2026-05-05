"""Custom widgets for TermWise TUI."""

from __future__ import annotations

import re
from datetime import datetime

from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    ProgressBar,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
    TextLog,
)


class MessageBubble(Static):
    """A chat message bubble widget."""

    role: reactive[str] = reactive("user")
    content: reactive[str] = reactive("")
    timestamp: reactive[str] = reactive("")

    def __init__(self, role: str = "user", content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.content = content
        self.timestamp = datetime.now().strftime("%H:%M:%S")

    def render(self) -> Panel:
        if self.role == "user":
            border_style = "blue"
            title = f"👤 You [{self.timestamp}]"
        elif self.role == "assistant":
            border_style = "green"
            title = f"🤖 Assistant [{self.timestamp}]"
        elif self.role == "system":
            border_style = "yellow"
            title = f"⚙️ System [{self.timestamp}]"
        elif self.role == "tool":
            border_style = "magenta"
            title = f"🔧 Tool [{self.timestamp}]"
        else:
            border_style = "white"
            title = f"📝 {self.role} [{self.timestamp}]"

        if self.role == "assistant":
            try:
                md = Markdown(self.content)
                return Panel(md, border_style=border_style, title=title, title_align="left")
            except Exception:
                pass

        return Panel(
            Text(self.content),
            border_style=border_style,
            title=title,
            title_align="left",
        )


class ChatLog(VerticalScroll):
    """Scrollable chat message log."""

    def add_message(self, role: str, content: str) -> MessageBubble:
        """Add a new message to the chat log."""
        bubble = MessageBubble(role=role, content=content)
        self.mount(bubble)
        self.scroll_end(animate=False)
        return bubble

    def add_streaming_message(self, role: str = "assistant") -> MessageBubble:
        """Add a message that will be streamed into."""
        bubble = MessageBubble(role=role, content="▌")
        self.mount(bubble)
        self.scroll_end(animate=False)
        return bubble

    def clear(self):
        """Clear all messages."""
        for child in list(self.children):
            child.remove()


class CodePreview(Static):
    """Code preview panel with syntax highlighting."""

    language: reactive[str] = reactive("python")
    code: reactive[str] = reactive("")

    def render(self) -> Syntax | Panel:
        if not self.code.strip():
            return Panel(
                Text("No code to preview", style="dim"),
                title="📄 Code Preview",
                border_style="dim",
            )
        try:
            syntax = Syntax(
                self.code,
                lexer=self.language,
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
            )
            return Panel(syntax, title=f"📄 {self.language}", border_style="cyan")
        except Exception:
            return Panel(
                Text(self.code),
                title=f"📄 {self.language}",
                border_style="cyan",
            )

    def set_code(self, code: str, language: str = "python"):
        """Set the code content and language."""
        self.language = language
        self.code = code


class StatusBar(Static):
    """Status bar showing current model, tokens, and cost."""

    model: reactive[str] = reactive("N/A")
    tokens_used: reactive[int] = reactive(0)
    total_cost: reactive[float] = reactive(0.0)
    is_generating: reactive[bool] = reactive(False)

    def render(self) -> Text:
        status = "🟢 Ready"
        if self.is_generating:
            status = "🔄 Generating..."

        text = Text()
        text.append(f"  {status}  ", style="bold")
        text.append("│ ", style="dim")
        text.append(f"🧠 Model: {self.model}  ", style="cyan")
        text.append("│ ", style="dim")
        text.append(f"📊 Tokens: {self.tokens_used:,}  ", style="green")
        text.append("│ ", style="dim")
        text.append(f"💰 Cost: ${self.total_cost:.4f}  ", style="yellow")
        return text


class InputArea(Container):
    """Multi-line input area with send button."""

    class Submitted(Message):
        """Message emitted when the user submits input."""
        def __init__(self, text: str):
            super().__init__()
            self.text = text

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._buffer = []

    def compose(self) -> ComposeResult:
        yield Label("💬 Message (Enter to send, Shift+Enter for new line):", classes="input-label")
        yield Input(placeholder="Type your message...", id="chat-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        text = event.value.strip()
        if text:
            self.post_message(self.Submitted(text))
            event.input.value = ""


class PlanView(Static):
    """View for displaying execution plans."""

    plan_text: reactive[str] = reactive("")

    def render(self) -> Panel:
        if not self.plan_text:
            return Panel(
                Text("No active plan", style="dim"),
                title="📋 Execution Plan",
                border_style="dim",
            )
        return Panel(
            Text.from_markup(self.plan_text),
            title="📋 Execution Plan",
            border_style="green",
        )

    def set_plan(self, plan_text: str):
        """Set the plan text."""
        self.plan_text = plan_text


class ModelSelector(ListView):
    """Model selection dropdown."""

    def __init__(self, models: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._models = models or []

    def set_models(self, models: list[str]):
        """Set the available models."""
        self._models = models
        self.clear()
        for model in models:
            self.mount(ListItem(Label(model)))
