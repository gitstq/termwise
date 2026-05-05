"""
文件写入工具

创建或修改文件内容。
"""

import os
from pathlib import Path
from typing import Any, Dict

from termwise.tools.base import BaseTool, ToolResult


class FileWriterTool(BaseTool):
    """文件写入工具。

    支持创建新文件、覆盖文件内容、追加内容等操作。
    """

    @property
    def name(self) -> str:
        """工具名称。"""
        return "write_file"

    @property
    def description(self) -> str:
        """工具描述。"""
        return (
            "写入内容到指定文件。如果文件已存在则覆盖内容，"
            "如果文件不存在则创建新文件。"
            "会自动创建必要的父目录。"
        )

    def parameters_schema(self) -> Dict[str, Any]:
        """参数JSON Schema。"""
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径（绝对路径或相对路径）",
                },
                "content": {
                    "type": "string",
                    "description": "要写入的文件内容",
                },
                "encoding": {
                    "type": "string",
                    "description": "文件编码，默认为utf-8",
                    "default": "utf-8",
                },
                "mode": {
                    "type": "string",
                    "description": "写入模式: 'write'覆盖写入, 'append'追加写入",
                    "default": "write",
                    "enum": ["write", "append"],
                },
            },
            "required": ["path", "content"],
        }

    def execute(self, **kwargs) -> ToolResult:
        """执行文件写入。

        Args:
            path: 文件路径
            content: 文件内容
            encoding: 文件编码
            mode: 写入模式

        Returns:
            ToolResult
        """
        file_path = kwargs.get("path", "")
        content = kwargs.get("content", "")
        encoding = kwargs.get("encoding", "utf-8")
        mode = kwargs.get("mode", "write")

        if not file_path:
            return ToolResult(success=False, error="文件路径不能为空")

        if content is None:
            return ToolResult(success=False, error="文件内容不能为空")

        # 解析路径
        path = Path(file_path)
        if not path.is_absolute():
            path = Path.cwd() / path

        try:
            path = path.resolve()
        except Exception as e:
            return ToolResult(success=False, error=f"路径解析失败: {e}")

        # 检查文件大小限制
        content_size = len(content.encode(encoding))
        max_size = 10 * 1024 * 1024  # 10MB限制
        if content_size > max_size:
            return ToolResult(
                success=False,
                error=f"内容过大 ({content_size} bytes)，最大支持 {max_size} bytes",
            )

        try:
            # 确保父目录存在
            path.parent.mkdir(parents=True, exist_ok=True)

            # 检查文件是否已存在
            file_existed = path.exists()

            # 写入文件
            write_mode = "a" if mode == "append" else "w"
            with open(path, write_mode, encoding=encoding) as f:
                f.write(content)

            bytes_written = len(content.encode(encoding))
            action = "追加到" if mode == "append" else ("覆盖了" if file_existed else "创建了")

            return ToolResult(
                success=True,
                output=f"成功{action}文件: {path} ({bytes_written} bytes)",
                metadata={
                    "path": str(path),
                    "bytes_written": bytes_written,
                    "mode": mode,
                    "file_existed": file_existed,
                },
            )

        except PermissionError:
            return ToolResult(success=False, error=f"没有权限写入文件: {path}")
        except Exception as e:
            return ToolResult(success=False, error=f"写入文件失败: {e}")
