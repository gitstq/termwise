"""Tests for Agent core."""

import json
import pytest
from unittest.mock import MagicMock, patch

from termwise.agent.core import AgentCore
from termwise.agent.conversation import ConversationManager
from termwise.agent.planner import TaskPlanner, ExecutionPlan, SubTask


class TestConversationManager:
    """Tests for ConversationManager."""

    def test_add_message(self):
        """Test adding a message."""
        manager = ConversationManager(max_context_tokens=1000)
        manager.add_message("user", "Hello!")
        assert len(manager.messages) == 1
        assert manager.messages[0]["role"] == "user"
        assert manager.messages[0]["content"] == "Hello!"

    def test_add_system_message(self):
        """Test adding a system message."""
        manager = ConversationManager(max_context_tokens=1000)
        manager.add_message("system", "You are helpful.")
        assert manager.messages[0]["role"] == "system"

    def test_get_messages(self):
        """Test getting messages in API format."""
        manager = ConversationManager(max_context_tokens=1000)
        manager.add_message("user", "Hi")
        manager.add_message("assistant", "Hello!")
        api_msgs = manager.get_messages()
        assert len(api_msgs) == 2
        assert api_msgs[0]["role"] == "user"
        assert api_msgs[1]["content"] == "Hello!"

    def test_context_trimming(self):
        """Test that old messages are trimmed when exceeding max tokens."""
        manager = ConversationManager(max_context_tokens=50)
        manager.add_message("system", "You are a coding assistant.")
        for i in range(20):
            manager.add_message("user", f"Message {i} with some extra content to use tokens")
            manager.add_message("assistant", f"Response {i} with some extra content to use tokens")

        api_msgs = manager.get_messages_for_api()
        assert api_msgs[0]["role"] == "system"
        assert len(api_msgs) < 42

    def test_clear(self):
        """Test clearing conversation."""
        manager = ConversationManager(max_context_tokens=1000)
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        manager.clear()
        assert len(manager.messages) == 0

    def test_message_count(self):
        """Test message count property."""
        manager = ConversationManager(max_context_tokens=1000)
        assert manager.message_count == 0
        manager.add_message("user", "Hi")
        assert manager.message_count == 1

    def test_is_empty(self):
        """Test is_empty property."""
        manager = ConversationManager(max_context_tokens=1000)
        assert manager.is_empty is True
        manager.add_message("user", "Hi")
        assert manager.is_empty is False

    def test_get_last_message(self):
        """Test getting last message."""
        manager = ConversationManager(max_context_tokens=1000)
        assert manager.get_last_message() is None
        manager.add_message("user", "First")
        manager.add_message("assistant", "Second")
        assert manager.get_last_message()["content"] == "Second"

    def test_add_tool_result(self):
        """Test adding tool result."""
        manager = ConversationManager(max_context_tokens=1000)
        manager.add_tool_result("read_file", "call_123", "file contents here")
        assert len(manager.messages) == 1
        assert manager.messages[0]["role"] == "tool"
        assert manager.messages[0]["tool_name"] == "read_file"

    def test_export_markdown(self):
        """Test exporting to markdown."""
        manager = ConversationManager(max_context_tokens=1000)
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        md = manager.export_markdown()
        assert "用户" in md
        assert "Hello" in md


class TestTaskPlanner:
    """Tests for TaskPlanner."""

    def test_rule_based_plan_create(self):
        """Test rule-based planning for create tasks."""
        planner = TaskPlanner()
        plan = planner.create_plan("Create a Python web scraper")
        assert plan.goal == "Create a Python web scraper"
        assert len(plan.sub_tasks) >= 3
        assert plan.sub_tasks[0].status == "pending"

    def test_rule_based_plan_fix(self):
        """Test rule-based planning for fix tasks."""
        planner = TaskPlanner()
        plan = planner.create_plan("Fix the login bug")
        assert "bug" in plan.goal.lower() or "fix" in plan.sub_tasks[0].description.lower()

    def test_rule_based_plan_refactor(self):
        """Test rule-based planning for refactor tasks."""
        planner = TaskPlanner()
        plan = planner.create_plan("Refactor the database module")
        assert len(plan.sub_tasks) >= 3

    def test_plan_progress(self):
        """Test plan progress calculation."""
        plan = ExecutionPlan(goal="Test")
        plan.add_task("Step 1")
        plan.add_task("Step 2")
        plan.add_task("Step 3")
        assert plan.progress() == 0.0

        plan.mark_completed(1)
        assert plan.progress() == pytest.approx(1 / 3)

        plan.mark_completed(2)
        plan.mark_completed(3)
        assert plan.is_complete() is True
        assert plan.progress() == 1.0

    def test_plan_serialization(self):
        """Test plan to_dict and from_dict."""
        plan = ExecutionPlan(goal="Test goal")
        plan.add_task("Step 1")
        plan.add_task("Step 2", dependencies=[1])

        data = plan.to_dict()
        restored = ExecutionPlan.from_dict(data)

        assert restored.goal == "Test goal"
        assert len(restored.sub_tasks) == 2
        assert restored.sub_tasks[1].dependencies == [1]

    def test_plan_summary(self):
        """Test plan summary output."""
        plan = ExecutionPlan(goal="Build something")
        plan.add_task("Step 1")
        plan.mark_completed(1, "Done")
        plan.add_task("Step 2")

        summary = plan.summary()
        assert "Build something" in summary
        assert "Step 1" in summary
        assert "Step 2" in summary

    def test_get_next_pending(self):
        """Test getting next pending task with dependencies."""
        plan = ExecutionPlan(goal="Test")
        plan.add_task("Step 1")
        plan.add_task("Step 2", dependencies=[1])
        plan.add_task("Step 3", dependencies=[2])

        next_task = plan.get_next_pending()
        assert next_task is not None
        assert next_task.id == 1

        plan.mark_completed(1)
        next_task = plan.get_next_pending()
        assert next_task.id == 2

    def test_mark_failed(self):
        """Test marking task as failed."""
        plan = ExecutionPlan(goal="Test")
        plan.add_task("Step 1")
        plan.mark_failed(1, "Something went wrong")
        assert plan.sub_tasks[0].status == "failed"
        assert plan.sub_tasks[0].error == "Something went wrong"


class TestAgentCore:
    """Tests for AgentCore."""

    def test_agent_init(self):
        """Test agent initialization."""
        mock_provider = MagicMock()
        mock_provider.get_default_model.return_value = "test-model"
        agent = AgentCore(provider=mock_provider)
        assert agent is not None
        assert agent.conversation is not None

    def test_agent_tools_loaded(self):
        """Test that agent can register tools."""
        mock_provider = MagicMock()
        mock_provider.get_default_model.return_value = "test-model"
        from termwise.tools.file_reader import FileReaderTool
        from termwise.tools.shell import ShellTool

        reader = FileReaderTool()
        shell = ShellTool()
        agent = AgentCore(provider=mock_provider, tools=[reader, shell])
        assert len(agent.tools) == 2
        assert "read_file" in agent.tools
        assert "shell" in agent.tools

    def test_agent_register_tool(self):
        """Test registering a tool."""
        mock_provider = MagicMock()
        mock_provider.get_default_model.return_value = "test-model"
        agent = AgentCore(provider=mock_provider)
        from termwise.tools.file_reader import FileReaderTool
        reader = FileReaderTool()
        agent.register_tool(reader)
        assert "read_file" in agent.tools

    def test_agent_unregister_tool(self):
        """Test unregistering a tool."""
        mock_provider = MagicMock()
        mock_provider.get_default_model.return_value = "test-model"
        from termwise.tools.file_reader import FileReaderTool
        reader = FileReaderTool()
        agent = AgentCore(provider=mock_provider, tools=[reader])
        agent.unregister_tool("read_file")
        assert "read_file" not in agent.tools

    def test_agent_new_conversation(self):
        """Test starting new conversation."""
        mock_provider = MagicMock()
        mock_provider.get_default_model.return_value = "test-model"
        agent = AgentCore(provider=mock_provider)
        agent.conversation.add_message("user", "Hello")
        agent.new_conversation()
        assert agent.conversation.is_empty
