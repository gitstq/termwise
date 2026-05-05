"""
工具基类

定义所有Agent工具的统一接口和基础功能。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """工具执行结果。

    Attributes:
        success: 是否执行成功
        output: 输出内容
        error: 错误信息（如果有）
        metadata: 附加元数据
    """
    success: bool
    output: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {"success": self.success, "output": self.output}
        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    def to_message(self) -> str:
        """转换为可发送给LLM的消息字符串。"""
        if self.success:
            return self.output
        return f"错误: {self.error}"


class BaseTool(ABC):
    """工具抽象基类。

    所有Agent可调用的工具必须继承此类。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称。"""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述，供LLM理解工具用途。"""
        raise NotImplementedError

    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """工具参数的JSON Schema描述。

        Returns:
            JSON Schema格式的参数描述
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """执行工具。

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult执行结果
        """
        raise NotImplementedError

    def to_openai_tool(self) -> Dict[str, Any]:
        """转换为OpenAI function calling格式的工具定义。

        Returns:
            OpenAI格式的工具定义字典
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema(),
            },
        }

    def validate_args(self, args: Dict[str, Any]) -> Optional[str]:
        """验证工具参数是否合法。

        Args:
            args: 参数字典

        Returns:
            错误信息字符串，None表示验证通过
        """
        schema = self.parameters_schema()
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # 检查必填参数
        for param_name in required:
            if param_name not in args or args[param_name] is None:
                return f"缺少必填参数: {param_name}"

        # 检查参数类型
        for param_name, value in args.items():
            if param_name in properties:
                expected_type = properties[param_name].get("type", "")
                if expected_type == "string" and not isinstance(value, str):
                    return f"参数 {param_name} 应为字符串类型"
                if expected_type == "integer" and not isinstance(value, int):
                    return f"参数 {param_name} 应为整数类型"
                if expected_type == "number" and not isinstance(value, (int, float)):
                    return f"参数 {param_name} 应为数字类型"
                if expected_type == "boolean" and not isinstance(value, bool):
                    return f"参数 {param_name} 应为布尔类型"

        return None
