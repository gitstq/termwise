"""
Shell命令执行工具

在终端中执行Shell命令并返回结果。
"""

import subprocess
import shlex
from typing import Any, Dict

from termwise.tools.base import BaseTool, ToolResult


class ShellTool(BaseTool):
    """Shell命令执行工具。

    执行Shell命令并捕获输出结果，支持超时控制。
    """

    # 危险命令黑名单
    DANGEROUS_COMMANDS = [
        "rm -rf /",
        "mkfs",
        "dd if=",
        ":(){ :|:& };:",
        "chmod -R 777 /",
        "chown -R",
        "> /dev/sda",
        "mv / /dev/null",
    ]

    def __init__(self, timeout: int = 30, working_dir: str = None):
        """初始化Shell工具。

        Args:
            timeout: 命令执行超时时间（秒）
            working_dir: 工作目录
        """
        self.timeout = timeout
        self.working_dir = working_dir

    @property
    def name(self) -> str:
        """工具名称。"""
        return "shell"

    @property
    def description(self) -> str:
        """工具描述。"""
        return (
            "执行Shell命令并返回输出结果。"
            "支持常见的Linux/macOS命令。"
            "命令执行有超时限制，长时间运行的命令可能被中断。"
            "注意：某些危险命令会被拒绝执行。"
        )

    def parameters_schema(self) -> Dict[str, Any]:
        """参数JSON Schema。"""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的Shell命令",
                },
                "timeout": {
                    "type": "integer",
                    "description": f"超时时间（秒），默认{self.timeout}秒",
                    "default": self.timeout,
                },
                "working_dir": {
                    "type": "string",
                    "description": "工作目录，默认为当前目录",
                },
            },
            "required": ["command"],
        }

    def _check_safety(self, command: str) -> str:
        """检查命令安全性。

        Args:
            command: 要检查的命令

        Returns:
            错误信息，空字符串表示安全
        """
        cmd_lower = command.lower().strip()
        for dangerous in self.DANGEROUS_COMMANDS:
            if dangerous in cmd_lower:
                return f"拒绝执行危险命令: 包含 '{dangerous}'"
        return ""

    def execute(self, **kwargs) -> ToolResult:
        """执行Shell命令。

        Args:
            command: Shell命令
            timeout: 超时时间
            working_dir: 工作目录

        Returns:
            ToolResult包含命令输出
        """
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", self.timeout)
        working_dir = kwargs.get("working_dir", self.working_dir)

        if not command:
            return ToolResult(success=False, error="命令不能为空")

        # 安全检查
        safety_error = self._check_safety(command)
        if safety_error:
            return ToolResult(success=False, error=safety_error)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                env=None,
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            return_code = result.returncode

            # 构建输出
            output_parts = []
            if stdout:
                output_parts.append(stdout)
            if stderr:
                output_parts.append(f"[stderr]\n{stderr}")

            output = "\n".join(output_parts) if output_parts else "(无输出)"

            # 限制输出长度
            max_output = 100000  # 100KB
            if len(output) > max_output:
                output = output[:max_output] + f"\n... (输出被截断，共 {len(output)} 字符)"

            success = return_code == 0
            error = "" if success else f"命令退出码: {return_code}"

            return ToolResult(
                success=success,
                output=output,
                error=error,
                metadata={
                    "return_code": return_code,
                    "command": command,
                },
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"命令执行超时 ({timeout}秒)",
                metadata={"command": command},
            )
        except Exception as e:
            return ToolResult(success=False, error=f"执行命令失败: {e}")
