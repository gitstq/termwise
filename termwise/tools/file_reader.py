"""
文件读取工具

读取指定路径的文件内容，支持行号范围和编码指定。
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from termwise.tools.base import BaseTool, ToolResult


class FileReaderTool(BaseTool):
    """文件读取工具。

    读取指定路径文件的内容，支持指定行号范围和编码。
    """

    @property
    def name(self) -> str:
        """工具名称。"""
        return "read_file"

    @property
    def description(self) -> str:
        """工具描述。"""
        return (
            "读取指定路径的文件内容。"
            "可以指定起始行和结束行来读取文件的部分内容。"
            "支持指定文件编码，默认使用UTF-8。"
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
                "offset": {
                    "type": "integer",
                    "description": "起始行号（从1开始），默认为1",
                    "default": 1,
                },
                "limit": {
                    "type": "integer",
                    "description": "读取的最大行数，默认读取全部",
                    "default": -1,
                },
                "encoding": {
                    "type": "string",
                    "description": "文件编码，默认为utf-8",
                    "default": "utf-8",
                },
            },
            "required": ["path"],
        }

    def execute(self, **kwargs) -> ToolResult:
        """执行文件读取。

        Args:
            path: 文件路径
            offset: 起始行号
            limit: 最大行数
            encoding: 文件编码

        Returns:
            ToolResult包含文件内容
        """
        file_path = kwargs.get("path", "")
        offset = kwargs.get("offset", 1)
        limit = kwargs.get("limit", -1)
        encoding = kwargs.get("encoding", "utf-8")

        if not file_path:
            return ToolResult(success=False, error="文件路径不能为空")

        # 解析路径
        path = Path(file_path)
        if not path.is_absolute():
            path = Path.cwd() / path

        # 安全检查：防止路径遍历
        try:
            path = path.resolve()
        except Exception as e:
            return ToolResult(success=False, error=f"路径解析失败: {e}")

        # 检查文件是否存在
        if not path.exists():
            return ToolResult(success=False, error=f"文件不存在: {path}")

        if not path.is_file():
            return ToolResult(success=False, error=f"路径不是文件: {path}")

        # 检查文件大小
        file_size = path.stat().st_size
        max_size = 10 * 1024 * 1024  # 10MB限制
        if file_size > max_size:
            return ToolResult(
                success=False,
                error=f"文件过大 ({file_size} bytes)，最大支持 {max_size} bytes",
            )

        try:
            with open(path, "r", encoding=encoding) as f:
                lines = f.readlines()

            total_lines = len(lines)

            # 处理行号范围
            start_idx = max(0, offset - 1)
            if limit == -1:
                end_idx = len(lines)
            else:
                end_idx = min(start_idx + limit, len(lines))

            selected_lines = lines[start_idx:end_idx]

            # 添加行号
            numbered_lines = []
            for i, line in enumerate(selected_lines, start=start_idx + 1):
                numbered_lines.append(f"{i:>6}\t{line.rstrip()}")

            content = "\n".join(numbered_lines)
            header = f"文件: {path} (共 {total_lines} 行)"
            if offset > 1 or limit != -1:
                header += f" [显示第 {start_idx + 1}-{end_idx} 行]"

            result_content = f"{header}\n{'=' * 60}\n{content}"

            return ToolResult(
                success=True,
                output=result_content,
                metadata={
                    "path": str(path),
                    "total_lines": total_lines,
                    "displayed_lines": len(selected_lines),
                    "encoding": encoding,
                },
            )

        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(path, "r", encoding="gbk") as f:
                    lines = f.readlines()
                content = "\n".join(
                    f"{i + 1:>6}\t{line.rstrip()}" for i, line in enumerate(lines)
                )
                return ToolResult(
                    success=True,
                    output=f"文件: {path} (编码: gbk)\n{'=' * 60}\n{content}",
                    metadata={"path": str(path), "encoding": "gbk"},
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"无法解码文件，请指定正确的编码: {e}",
                )
        except Exception as e:
            return ToolResult(success=False, error=f"读取文件失败: {e}")
