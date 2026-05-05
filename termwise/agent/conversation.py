"""
对话管理模块

管理对话历史，包括消息的添加、获取、裁剪和持久化。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConversationManager:
    """对话管理器。

    负责管理对话消息的存储、检索和上下文窗口管理。
    """

    def __init__(
        self,
        max_context_tokens: int = 128000,
        save_dir: Optional[str] = None,
    ):
        """初始化对话管理器。

        Args:
            max_context_tokens: 最大上下文token数
            save_dir: 对话保存目录
        """
        self.max_context_tokens = max_context_tokens
        self.save_dir = Path(save_dir) if save_dir else Path.home() / ".termwise" / "conversations"
        self.messages: List[Dict[str, Any]] = []
        self.created_at: Optional[datetime] = None
        self.title: str = "新对话"

    def add_message(self, role: str, content: str) -> None:
        """添加一条消息到对话。

        Args:
            role: 消息角色 (user, assistant, system, tool)
            content: 消息内容
        """
        if not self.created_at:
            self.created_at = datetime.now()

        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

        # 自动设置标题
        if role == "user" and len(self.messages) == 1:
            self.title = content[:50] + ("..." if len(content) > 50 else "")

    def add_tool_result(
        self,
        tool_name: str,
        tool_id: str,
        result: str,
    ) -> None:
        """添加工具调用结果到对话。

        Args:
            tool_name: 工具名称
            tool_id: 工具调用ID
            result: 工具执行结果
        """
        self.messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "tool_call_id": tool_id,
            "content": result,
            "timestamp": datetime.now().isoformat(),
        })

    def get_messages(self, max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
        """获取对话消息列表。

        Args:
            max_tokens: 最大token数限制，None则使用默认值

        Returns:
            消息列表（仅包含role和content）
        """
        messages = []
        for msg in self.messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
        return messages

    def get_messages_for_api(self, max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
        """获取用于API调用的消息列表，自动裁剪以适应上下文窗口。

        Args:
            max_tokens: 最大token数限制

        Returns:
            裁剪后的消息列表
        """
        limit = max_tokens or self.max_context_tokens
        messages = self.get_messages()

        # 简单的token估算（约4字符=1token）
        estimated_tokens = sum(
            len(msg.get("content", "")) // 4 for msg in messages
        )

        if estimated_tokens <= limit:
            return messages

        # 从最早的消息开始裁剪（保留系统消息和最近的对话）
        result = []
        total_tokens = 0

        # 保留系统消息
        for msg in messages:
            if msg["role"] == "system":
                result.append(msg)
                total_tokens += len(msg.get("content", "")) // 4

        # 从最近的对话开始添加
        for msg in reversed(messages):
            if msg["role"] == "system":
                continue
            msg_tokens = len(msg.get("content", "")) // 4
            if total_tokens + msg_tokens > limit:
                break
            result.insert(1 if len(result) > 0 else 0, msg)
            total_tokens += msg_tokens

        return result

    def clear(self) -> None:
        """清空对话历史。"""
        self.messages.clear()
        self.created_at = None
        self.title = "新对话"

    @property
    def message_count(self) -> int:
        """获取消息数量。"""
        return len(self.messages)

    @property
    def is_empty(self) -> bool:
        """对话是否为空。"""
        return len(self.messages) == 0

    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """获取最后一条消息。"""
        return self.messages[-1] if self.messages else None

    def get_user_messages(self) -> List[Dict[str, Any]]:
        """获取所有用户消息。"""
        return [msg for msg in self.messages if msg["role"] == "user"]

    def get_assistant_messages(self) -> List[Dict[str, Any]]:
        """获取所有助手消息。"""
        return [msg for msg in self.messages if msg["role"] == "assistant"]

    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """获取所有工具调用记录。"""
        return [msg for msg in self.messages if msg["role"] == "tool"]

    def save(self, filename: Optional[str] = None) -> str:
        """保存对话到文件。

        Args:
            filename: 文件名，None则自动生成

        Returns:
            保存的文件路径
        """
        self.save_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"

        filepath = self.save_dir / filename
        data = {
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "messages": self.messages,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def load(self, filepath: str) -> bool:
        """从文件加载对话。

        Args:
            filepath: 文件路径

        Returns:
            是否加载成功
        """
        path = Path(filepath)
        if not path.exists():
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.title = data.get("title", "加载的对话")
            created = data.get("created_at")
            self.created_at = datetime.fromisoformat(created) if created else None
            self.messages = data.get("messages", [])
            return True
        except Exception:
            return False

    def list_saved_conversations(self) -> List[Dict[str, Any]]:
        """列出所有已保存的对话。

        Returns:
            对话信息列表
        """
        conversations = []
        if not self.save_dir.exists():
            return conversations

        for filepath in sorted(self.save_dir.glob("conversation_*.json"), reverse=True):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conversations.append({
                    "path": str(filepath),
                    "title": data.get("title", "无标题"),
                    "created_at": data.get("created_at", ""),
                    "message_count": len(data.get("messages", [])),
                })
            except Exception:
                continue

        return conversations

    def export_markdown(self) -> str:
        """将对话导出为Markdown格式。

        Returns:
            Markdown格式的对话内容
        """
        lines = [f"# {self.title}\n"]
        if self.created_at:
            lines.append(f"*创建时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}*\n")

        for msg in self.messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user":
                lines.append(f"## 用户\n\n{content}\n")
            elif role == "assistant":
                lines.append(f"## 助手\n\n{content}\n")
            elif role == "tool":
                tool_name = msg.get("tool_name", "unknown")
                lines.append(f"### 工具: {tool_name}\n\n```\n{content}\n```\n")
            elif role == "system":
                lines.append(f"<!-- 系统消息 -->\n")

        return "\n".join(lines)
