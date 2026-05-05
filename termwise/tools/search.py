"""
代码搜索工具

在项目中搜索代码，支持文件名搜索和内容搜索。
"""

import os
import re
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional

from termwise.tools.base import BaseTool, ToolResult


class SearchTool(BaseTool):
    """代码搜索工具。

    支持按文件名模式搜索和按内容正则搜索。
    """

    # 默认忽略的目录
    DEFAULT_IGNORE_DIRS = {
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        ".tox", ".mypy_cache", ".pytest_cache", ".eggs", "*.egg-info",
        "dist", "build", ".idea", ".vscode",
    }

    # 默认忽略的文件模式
    DEFAULT_IGNORE_PATTERNS = {
        "*.pyc", "*.pyo", "*.so", "*.dylib", "*.dll",
        "*.exe", "*.bin", "*.dat", "*.lock",
        ".DS_Store", "Thumbs.db",
    }

    def __init__(self, working_dir: str = None, max_results: int = 50):
        """初始化搜索工具。

        Args:
            working_dir: 搜索根目录
            max_results: 最大结果数量
        """
        self.working_dir = working_dir or str(Path.cwd())
        self.max_results = max_results

    @property
    def name(self) -> str:
        """工具名称。"""
        return "search"

    @property
    def description(self) -> str:
        """工具描述。"""
        return (
            "在项目中搜索代码。支持两种模式：\n"
            "1. 文件名搜索: 按文件名模式（支持通配符）查找文件\n"
            "2. 内容搜索: 在文件内容中搜索匹配正则表达式的行\n"
            "可以指定文件类型过滤（如只搜索.py文件）。"
        )

    def parameters_schema(self) -> Dict[str, Any]:
        """参数JSON Schema。"""
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "搜索模式：文件名模式（通配符）或内容正则表达式",
                },
                "search_type": {
                    "type": "string",
                    "description": "搜索类型: 'filename'搜索文件名, 'content'搜索文件内容",
                    "default": "content",
                    "enum": ["filename", "content"],
                },
                "path": {
                    "type": "string",
                    "description": "搜索的根目录，默认为当前目录",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "文件过滤模式（通配符），如 '*.py', '*.js'",
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大结果数量，默认50",
                    "default": 50,
                },
                "include_hidden": {
                    "type": "boolean",
                    "description": "是否包含隐藏文件和目录",
                    "default": False,
                },
            },
            "required": ["pattern"],
        }

    def _should_ignore(self, path: Path, include_hidden: bool) -> bool:
        """判断路径是否应该被忽略。

        Args:
            path: 文件或目录路径
            include_hidden: 是否包含隐藏文件

        Returns:
            是否应该忽略
        """
        name = path.name

        # 隐藏文件/目录
        if not include_hidden and name.startswith("."):
            return True

        # 忽略的目录
        if path.is_dir() and name in self.DEFAULT_IGNORE_DIRS:
            return True

        # 忽略的文件模式
        for pattern in self.DEFAULT_IGNORE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True

        return False

    def _search_filename(
        self,
        pattern: str,
        root_dir: Path,
        file_pattern: Optional[str],
        max_results: int,
        include_hidden: bool,
    ) -> List[Dict[str, str]]:
        """按文件名搜索。

        Args:
            pattern: 文件名模式（通配符）
            root_dir: 搜索根目录
            file_pattern: 额外的文件过滤
            max_results: 最大结果数
            include_hidden: 是否包含隐藏文件

        Returns:
            匹配的文件列表
        """
        results = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            current_dir = Path(dirpath)

            # 过滤目录
            dirnames[:] = [
                d for d in dirnames
                if not self._should_ignore(current_dir / d, include_hidden)
            ]

            for filename in filenames:
                file_path = current_dir / filename

                if self._should_ignore(file_path, include_hidden):
                    continue

                # 匹配文件名模式
                if fnmatch.fnmatch(filename, pattern):
                    # 额外的文件类型过滤
                    if file_pattern and not fnmatch.fnmatch(filename, file_pattern):
                        continue

                    results.append({
                        "path": str(file_path),
                        "name": filename,
                    })

                    if len(results) >= max_results:
                        return results

        return results

    def _search_content(
        self,
        pattern: str,
        root_dir: Path,
        file_pattern: Optional[str],
        max_results: int,
        include_hidden: bool,
    ) -> List[Dict[str, Any]]:
        """按文件内容搜索。

        Args:
            pattern: 正则表达式
            root_dir: 搜索根目录
            file_pattern: 文件过滤
            max_results: 最大结果数
            include_hidden: 是否包含隐藏文件

        Returns:
            匹配结果列表
        """
        results = []
        total_matches = 0

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return [{"error": f"无效的正则表达式: {e}"}]

        # 文本文件扩展名
        TEXT_EXTENSIONS = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
            ".toml", ".cfg", ".ini", ".md", ".txt", ".rst", ".html", ".css",
            ".scss", ".less", ".go", ".rs", ".java", ".kt", ".swift", ".c",
            ".cpp", ".h", ".hpp", ".sh", ".bash", ".zsh", ".fish",
            ".sql", ".r", ".rb", ".php", ".pl", ".lua", ".vim",
            ".dockerfile", ".makefile", ".cmake",
        }

        for dirpath, dirnames, filenames in os.walk(root_dir):
            current_dir = Path(dirpath)

            # 过滤目录
            dirnames[:] = [
                d for d in dirnames
                if not self._should_ignore(current_dir / d, include_hidden)
            ]

            for filename in filenames:
                file_path = current_dir / filename

                if self._should_ignore(file_path, include_hidden):
                    continue

                # 文件类型过滤
                if file_pattern and not fnmatch.fnmatch(filename, file_pattern):
                    continue

                # 只搜索文本文件
                ext = file_path.suffix.lower()
                if ext and ext not in TEXT_EXTENSIONS:
                    # 也检查没有扩展名的文件
                    if ext:
                        continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "path": str(file_path),
                                    "line": line_num,
                                    "content": line.rstrip(),
                                    "match": regex.search(line).group() if regex.search(line) else "",
                                })
                                total_matches += 1

                                if total_matches >= max_results:
                                    return results
                except (IOError, OSError):
                    continue

        return results

    def execute(self, **kwargs) -> ToolResult:
        """执行搜索。

        Args:
            pattern: 搜索模式
            search_type: 搜索类型
            path: 搜索根目录
            file_pattern: 文件过滤模式
            max_results: 最大结果数
            include_hidden: 是否包含隐藏文件

        Returns:
            ToolResult
        """
        pattern = kwargs.get("pattern", "")
        search_type = kwargs.get("search_type", "content")
        search_path = kwargs.get("path", self.working_dir)
        file_pattern = kwargs.get("file_pattern")
        max_results = kwargs.get("max_results", self.max_results)
        include_hidden = kwargs.get("include_hidden", False)

        if not pattern:
            return ToolResult(success=False, error="搜索模式不能为空")

        root_dir = Path(search_path)
        if not root_dir.is_absolute():
            root_dir = Path.cwd() / root_dir

        if not root_dir.exists():
            return ToolResult(success=False, error=f"目录不存在: {root_dir}")

        try:
            if search_type == "filename":
                results = self._search_filename(
                    pattern, root_dir, file_pattern, max_results, include_hidden
                )
                if not results:
                    return ToolResult(
                        success=True,
                        output=f"未找到匹配 '{pattern}' 的文件",
                    )

                output_lines = [f"找到 {len(results)} 个匹配文件:\n"]
                for r in results:
                    output_lines.append(f"  {r['path']}")
                output = "\n".join(output_lines)

                return ToolResult(
                    success=True,
                    output=output,
                    metadata={"match_count": len(results), "search_type": "filename"},
                )

            else:  # content search
                results = self._search_content(
                    pattern, root_dir, file_pattern, max_results, include_hidden
                )

                if results and "error" in results[0]:
                    return ToolResult(success=False, error=results[0]["error"])

                if not results:
                    return ToolResult(
                        success=True,
                        output=f"未找到匹配 '{pattern}' 的内容",
                    )

                output_lines = [f"找到 {len(results)} 处匹配:\n"]
                for r in results:
                    output_lines.append(
                        f"  {r['path']}:{r['line']}: {r['content']}"
                    )
                output = "\n".join(output_lines)

                return ToolResult(
                    success=True,
                    output=output,
                    metadata={"match_count": len(results), "search_type": "content"},
                )

        except Exception as e:
            return ToolResult(success=False, error=f"搜索失败: {e}")
