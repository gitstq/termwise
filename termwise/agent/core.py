"""
Agent核心逻辑

实现ReAct（Reasoning + Acting）模式的AI代理。
通过思考->行动->观察的循环来处理用户请求。
"""

import json
from typing import Any, Callable, Dict, List, Optional

from termwise.providers.base import BaseProvider
from termwise.tools.base import BaseTool, ToolResult
from termwise.agent.conversation import ConversationManager
from termwise.utils.cost_tracker import CostTracker


# 系统提示词
SYSTEM_PROMPT = """你是一个强大的AI编码助手，运行在终端环境中。你可以使用以下工具来帮助用户完成任务：

{tool_descriptions}

工作流程：
1. 仔细分析用户的需求
2. 思考需要哪些步骤来完成
3. 使用适当的工具执行操作
4. 根据工具返回的结果继续下一步
5. 最终给出完整的回答

注意事项：
- 在执行操作前先思考，确保操作是正确的
- 如果不确定，可以先读取文件确认内容
- 修改文件时要小心，确保不破坏现有功能
- 给出清晰、准确的回答
- 使用中文回答用户的问题

当你需要使用工具时，请通过工具调用来执行，不要手动模拟工具的输出。"""


class AgentCore:
    """Agent核心类。

    实现ReAct模式的AI代理，协调LLM推理和工具调用。
    """

    def __init__(
        self,
        provider: BaseProvider,
        tools: Optional[List[BaseTool]] = None,
        conversation: Optional[ConversationManager] = None,
        cost_tracker: Optional[CostTracker] = None,
        max_iterations: int = 20,
        model: Optional[str] = None,
    ):
        """初始化Agent。

        Args:
            provider: LLM Provider实例
            tools: 可用工具列表
            conversation: 对话管理器
            cost_tracker: 费用追踪器
            max_iterations: 最大迭代次数
            model: 使用的模型名称
        """
        self.provider = provider
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.conversation = conversation or ConversationManager()
        self.cost_tracker = cost_tracker
        self.max_iterations = max_iterations
        self.model = model or provider.get_default_model()
        self._is_running = False
        self._on_tool_call: Optional[Callable] = None
        self._on_response: Optional[Callable] = None
        self._on_thinking: Optional[Callable] = None

    @property
    def tool_list(self) -> List[BaseTool]:
        """获取工具列表。"""
        return list(self.tools.values())

    def register_tool(self, tool: BaseTool) -> None:
        """注册一个工具。

        Args:
            tool: 工具实例
        """
        self.tools[tool.name] = tool

    def unregister_tool(self, name: str) -> None:
        """取消注册一个工具。

        Args:
            name: 工具名称
        """
        self.tools.pop(name, None)

    def set_callback(
        self,
        on_tool_call: Optional[Callable] = None,
        on_response: Optional[Callable] = None,
        on_thinking: Optional[Callable] = None,
    ) -> None:
        """设置回调函数。

        Args:
            on_tool_call: 工具调用回调
            on_response: 响应生成回调
            on_thinking: 思考过程回调
        """
        self._on_tool_call = on_tool_call
        self._on_response = on_response
        self._on_thinking = on_thinking

    def _build_tool_descriptions(self) -> str:
        """构建工具描述文本。

        Returns:
            工具描述字符串
        """
        if not self.tools:
            return "当前没有可用的工具。"

        descriptions = []
        for tool in self.tools.values():
            schema = tool.parameters_schema()
            params_desc = []
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            for param_name, param_info in properties.items():
                req = " (必填)" if param_name in required else " (可选)"
                params_desc.append(
                    f"    - {param_name}{req}: {param_info.get('description', '')}"
                )
            desc = f"- {tool.name}: {tool.description}\n  参数:\n" + "\n".join(params_desc)
            descriptions.append(desc)

        return "\n".join(descriptions)

    def _build_system_message(self) -> Dict[str, str]:
        """构建系统消息。

        Returns:
            系统消息字典
        """
        tool_descriptions = self._build_tool_descriptions()
        content = SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions)
        return {"role": "system", "content": content}

    def _get_openai_tools(self) -> List[Dict[str, Any]]:
        """获取OpenAI格式的工具定义列表。

        Returns:
            工具定义列表
        """
        return [tool.to_openai_tool() for tool in self.tools.values()]

    def _execute_tool(self, tool_name: str, arguments: str) -> ToolResult:
        """执行工具调用。

        Args:
            tool_name: 工具名称
            arguments: JSON格式的参数字符串

        Returns:
            工具执行结果
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"未知工具: {tool_name}，可用工具: {', '.join(self.tools.keys())}",
            )

        # 解析参数
        try:
            args = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError as e:
            return ToolResult(success=False, error=f"参数JSON解析失败: {e}")

        # 验证参数
        validation_error = tool.validate_args(args)
        if validation_error:
            return ToolResult(success=False, error=validation_error)

        # 通知回调
        if self._on_tool_call:
            self._on_tool_call(tool_name, args)

        # 执行工具
        try:
            result = tool.execute(**args)
            return result
        except Exception as e:
            return ToolResult(success=False, error=f"工具执行异常: {e}")

    def _record_cost(self, provider_name: str, model: str) -> None:
        """记录API调用费用。

        Args:
            provider_name: Provider名称
            model: 模型名称
        """
        if self.cost_tracker and self.provider.last_usage:
            usage = self.provider.last_usage
            cost = self.provider.estimate_cost(usage)
            self.cost_tracker.record_usage(
                provider=provider_name,
                model=model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                cost=cost,
            )

    async def chat(self, user_message: str) -> str:
        """异步处理用户消息（ReAct循环）。

        Args:
            user_message: 用户消息

        Returns:
            最终回复内容
        """
        self._is_running = True

        # 添加用户消息到对话
        self.conversation.add_message("user", user_message)

        iteration = 0
        final_response = ""

        while self._is_running and iteration < self.max_iterations:
            iteration += 1

            # 构建消息列表
            messages = [self._build_system_message()]
            messages.extend(self.conversation.get_messages())

            # 通知思考回调
            if self._on_thinking:
                self._on_thinking(f"迭代 {iteration}...")

            try:
                if self.tools:
                    # 带工具调用的请求
                    result = self.provider.complete_with_tools(
                        messages=messages,
                        tools=self._get_openai_tools(),
                        model=self.model,
                    )
                else:
                    # 纯文本请求
                    content = self.provider.complete(
                        messages=messages,
                        model=self.model,
                    )
                    result = {"content": content, "tool_calls": []}

            except Exception as e:
                error_msg = f"LLM请求失败: {e}"
                self.conversation.add_message("assistant", f"抱歉，{error_msg}")
                return error_msg

            # 记录费用
            self._record_cost(self.provider.name, self.model)

            content = result.get("content", "")
            tool_calls = result.get("tool_calls", [])

            # 如果没有工具调用，直接返回回复
            if not tool_calls:
                final_response = content
                self.conversation.add_message("assistant", content)
                if self._on_response:
                    self._on_response(content)
                break

            # 处理工具调用
            # 先添加助手消息（包含工具调用）
            assistant_msg = {"role": "assistant", "content": content or None}

            if self._on_response and content:
                self._on_response(content)

            # 执行每个工具调用
            for tc in tool_calls:
                tool_name = tc.get("name", "")
                tool_args = tc.get("arguments", "{}")
                tool_id = tc.get("id", "")

                if self._on_thinking:
                    self._on_thinking(f"调用工具: {tool_name}")

                # 执行工具
                tool_result = self._execute_tool(tool_name, tool_args)

                # 将工具结果添加到对话
                self.conversation.add_tool_result(
                    tool_name=tool_name,
                    tool_id=tool_id,
                    result=tool_result.to_message(),
                )

        if iteration >= self.max_iterations:
            final_response = content + "\n\n[已达到最大迭代次数]"
            self.conversation.add_message("assistant", final_response)

        self._is_running = False
        return final_response

    def stop(self) -> None:
        """停止当前运行。"""
        self._is_running = False

    def new_conversation(self) -> None:
        """开始新对话。"""
        self.conversation.clear()

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史。"""
        return self.conversation.get_messages()
