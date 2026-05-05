"""Tests for tool system."""

import json
import os
import tempfile
import pytest
from pathlib import Path

from termwise.tools.base import BaseTool, ToolResult
from termwise.tools.file_reader import FileReaderTool
from termwise.tools.file_writer import FileWriterTool
from termwise.tools.shell import ShellTool
from termwise.tools.search import SearchTool


class TestBaseTool:
    """Tests for BaseTool."""

    def test_base_tool_interface(self):
        """Test that BaseTool defines required interface."""
        assert hasattr(BaseTool, "name")
        assert hasattr(BaseTool, "description")
        assert hasattr(BaseTool, "parameters_schema")
        assert hasattr(BaseTool, "execute")

    def test_tool_result_creation(self):
        """Test ToolResult creation."""
        result = ToolResult(success=True, output="test output")
        assert result.success is True
        assert result.output == "test output"
        assert result.error == ""

    def test_tool_result_failure(self):
        """Test ToolResult for failure case."""
        result = ToolResult(success=False, output="", error="Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"

    def test_tool_result_to_dict(self):
        """Test ToolResult serialization."""
        result = ToolResult(success=True, output="hello")
        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] == "hello"

    def test_tool_result_to_message(self):
        """Test ToolResult to_message."""
        result_ok = ToolResult(success=True, output="file contents here")
        assert result_ok.to_message() == "file contents here"

        result_err = ToolResult(success=False, error="file not found")
        assert "file not found" in result_err.to_message()


class TestFileReader:
    """Tests for FileReaderTool."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello world')\n")
            f.flush()
            path = f.name

        try:
            reader = FileReaderTool()
            result = reader.execute(path=path)
            assert result.success is True
            assert "hello world" in result.output
        finally:
            os.unlink(path)

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        reader = FileReaderTool()
        result = reader.execute(path="/nonexistent/file.txt")
        assert result.success is False

    def test_read_with_line_range(self):
        """Test reading specific lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("line1\nline2\nline3\nline4\nline5\n")
            f.flush()
            path = f.name

        try:
            reader = FileReaderTool()
            result = reader.execute(path=path, offset=2, limit=3)
            assert result.success is True
            assert "line2" in result.output
            assert "line4" in result.output
            assert "line1" not in result.output
        finally:
            os.unlink(path)

    def test_file_reader_schema(self):
        """Test FileReaderTool has valid schema."""
        reader = FileReaderTool()
        schema = reader.parameters_schema()
        assert schema["type"] == "object"
        assert "path" in schema["properties"]

    def test_file_reader_name(self):
        """Test FileReaderTool name."""
        reader = FileReaderTool()
        assert reader.name == "read_file"


class TestFileWriter:
    """Tests for FileWriterTool."""

    def test_write_new_file(self):
        """Test writing a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_file.py")
            writer = FileWriterTool()
            result = writer.execute(
                path=path,
                content="x = 42\nprint(x)\n",
            )
            assert result.success is True
            assert os.path.exists(path)
            with open(path) as f:
                assert "x = 42" in f.read()

    def test_write_empty_path(self):
        """Test writing with empty path."""
        writer = FileWriterTool()
        result = writer.execute(path="", content="test")
        assert result.success is False

    def test_file_writer_name(self):
        """Test FileWriterTool name."""
        writer = FileWriterTool()
        assert writer.name == "write_file"


class TestShellExecutor:
    """Tests for ShellTool."""

    def test_execute_simple_command(self):
        """Test executing a simple command."""
        executor = ShellTool()
        result = executor.execute(command="echo hello")
        assert result.success is True
        assert "hello" in result.output

    def test_execute_invalid_command(self):
        """Test executing an invalid command."""
        executor = ShellTool(timeout=5)
        result = executor.execute(command="nonexistent_command_xyz_123")
        assert result.success is False

    def test_blocked_command(self):
        """Test that dangerous commands are blocked."""
        executor = ShellTool()
        result = executor.execute(command="rm -rf /")
        assert result.success is False
        assert "危险" in result.error or "danger" in result.error.lower()

    def test_empty_command(self):
        """Test empty command."""
        executor = ShellTool()
        result = executor.execute(command="")
        assert result.success is False

    def test_shell_name(self):
        """Test ShellTool name."""
        executor = ShellTool()
        assert executor.name == "shell"


class TestCodeSearcher:
    """Tests for SearchTool."""

    def test_search_in_directory(self):
        """Test searching for code in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("def hello():\n    print('world')\n")

            searcher = SearchTool()
            result = searcher.execute(
                path=tmpdir,
                pattern="hello",
            )
            assert result.success is True
            assert "hello" in result.output

    def test_search_nonexistent_directory(self):
        """Test searching in a non-existent directory."""
        searcher = SearchTool()
        result = searcher.execute(
            path="/nonexistent/dir",
            pattern="test",
        )
        assert result.success is False

    def test_search_filename(self):
        """Test filename search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "my_script.py")
            with open(test_file, "w") as f:
                f.write("pass\n")

            searcher = SearchTool()
            result = searcher.execute(
                path=tmpdir,
                pattern="*.py",
                search_type="filename",
            )
            assert result.success is True
            assert "my_script.py" in result.output

    def test_search_name(self):
        """Test SearchTool name."""
        searcher = SearchTool()
        assert searcher.name == "search"
