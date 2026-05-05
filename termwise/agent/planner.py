"""Task planner for breaking down complex coding tasks into sub-steps."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SubTask:
    """A single sub-task in the execution plan."""

    id: int
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    dependencies: List[int] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "dependencies": self.dependencies,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SubTask":
        return cls(
            id=data["id"],
            description=data["description"],
            status=data.get("status", "pending"),
            dependencies=data.get("dependencies", []),
            result=data.get("result"),
            error=data.get("error"),
        )


@dataclass
class ExecutionPlan:
    """An execution plan consisting of ordered sub-tasks."""

    goal: str
    sub_tasks: List[SubTask] = field(default_factory=list)
    current_index: int = 0

    def add_task(self, description: str, dependencies: Optional[List[int]] = None) -> SubTask:
        """Add a new sub-task to the plan."""
        task_id = len(self.sub_tasks) + 1
        task = SubTask(
            id=task_id,
            description=description,
            dependencies=dependencies or [],
        )
        self.sub_tasks.append(task)
        return task

    def get_next_pending(self) -> Optional[SubTask]:
        """Get the next pending task whose dependencies are all completed."""
        for task in self.sub_tasks:
            if task.status != "pending":
                continue
            deps_met = all(
                self.sub_tasks[d - 1].status == "completed"
                for d in task.dependencies
                if 0 < d <= len(self.sub_tasks)
            )
            if deps_met:
                return task
        return None

    def get_current_task(self) -> Optional[SubTask]:
        """Get the currently active task."""
        for task in self.sub_tasks:
            if task.status == "in_progress":
                return task
        return None

    def mark_completed(self, task_id: int, result: Optional[str] = None):
        """Mark a task as completed."""
        for task in self.sub_tasks:
            if task.id == task_id:
                task.status = "completed"
                task.result = result
                break

    def mark_failed(self, task_id: int, error: str):
        """Mark a task as failed."""
        for task in self.sub_tasks:
            if task.id == task_id:
                task.status = "failed"
                task.error = error
                break

    def is_complete(self) -> bool:
        """Check if all tasks are completed."""
        return all(t.status == "completed" for t in self.sub_tasks)

    def progress(self) -> float:
        """Get progress as a fraction (0.0 to 1.0)."""
        if not self.sub_tasks:
            return 0.0
        completed = sum(1 for t in self.sub_tasks if t.status == "completed")
        return completed / len(self.sub_tasks)

    def summary(self) -> str:
        """Get a human-readable summary of the plan."""
        lines = [f"📋 Plan: {self.goal}", ""]
        for task in self.sub_tasks:
            status_icon = {
                "pending": "⬜",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌",
            }.get(task.status, "⬜")
            dep_str = f" (after: {task.dependencies})" if task.dependencies else ""
            lines.append(f"  {status_icon} [{task.id}] {task.description}{dep_str}")
            if task.error:
                lines.append(f"      ❗ Error: {task.error}")
        lines.append(f"\n📊 Progress: {self.progress() * 100:.0f}%")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "sub_tasks": [t.to_dict() for t in self.sub_tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionPlan":
        plan = cls(goal=data["goal"])
        for t_data in data.get("sub_tasks", []):
            plan.sub_tasks.append(SubTask.from_dict(t_data))
        return plan


class TaskPlanner:
    """Plans complex coding tasks by decomposing them into executable sub-steps."""

    PLAN_SYSTEM_PROMPT = """You are a task planning assistant. Given a user's coding request,
break it down into clear, ordered sub-tasks. Each sub-task should be:
1. Specific and actionable
2. Independently verifiable
3. Ordered by dependency (later tasks may depend on earlier ones)

Respond ONLY with a valid JSON object in this exact format:
{
  "goal": "Brief summary of the overall goal",
  "steps": [
    {"description": "Step 1 description", "depends_on": []},
    {"description": "Step 2 description", "depends_on": [1]},
    {"description": "Step 3 description", "depends_on": [1, 2]}
  ]
}

Rules:
- First step should always have depends_on: []
- Dependencies reference step numbers (1-indexed)
- Keep steps granular but not overly so (5-15 steps is ideal)
- Each step should be completable by an AI coding agent with file read/write/shell tools"""

    def __init__(self, provider=None):
        """Initialize the planner with an optional LLM provider.

        Args:
            provider: An LLM provider instance for AI-powered planning.
                     If None, uses rule-based planning.
        """
        self._provider = provider

    def create_plan(self, task_description: str) -> ExecutionPlan:
        """Create an execution plan for the given task.

        Args:
            task_description: The user's task description.

        Returns:
            An ExecutionPlan with ordered sub-tasks.
        """
        if self._provider:
            return self._ai_plan(task_description)
        return self._rule_based_plan(task_description)

    def _ai_plan(self, task_description: str) -> ExecutionPlan:
        """Use LLM to create a plan."""
        try:
            messages = [
                {"role": "system", "content": self.PLAN_SYSTEM_PROMPT},
                {"role": "user", "content": f"Break down this task:\n\n{task_description}"},
            ]
            response = self._provider.complete(messages=messages, model="", max_tokens=2000)
            plan_data = self._parse_plan_response(response)
            return self._build_plan_from_parsed(task_description, plan_data)
        except Exception:
            return self._rule_based_plan(task_description)

    def _parse_plan_response(self, response: str) -> dict:
        """Parse the LLM response into a structured plan."""
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            return json.loads(json_match.group())
        return {"goal": "", "steps": []}

    def _build_plan_from_parsed(self, task_description: str, data: dict) -> ExecutionPlan:
        """Build an ExecutionPlan from parsed LLM response."""
        plan = ExecutionPlan(goal=data.get("goal", task_description))
        for step in data.get("steps", []):
            deps = step.get("depends_on", [])
            if isinstance(deps, int):
                deps = [deps]
            plan.add_task(step["description"], dependencies=deps)
        if not plan.sub_tasks:
            return self._rule_based_plan(task_description)
        return plan

    def _rule_based_plan(self, task_description: str) -> ExecutionPlan:
        """Create a plan using rule-based heuristics when no LLM is available."""
        plan = ExecutionPlan(goal=task_description)

        desc_lower = task_description.lower()

        if any(kw in desc_lower for kw in ["create", "build", "make", "write", "develop"]):
            plan.add_task("Analyze requirements and understand the task scope")
            plan.add_task("Design the project structure and architecture")
            plan.add_task("Set up the project skeleton and configuration files", dependencies=[2])
            plan.add_task("Implement core functionality", dependencies=[3])
            plan.add_task("Add error handling and edge cases", dependencies=[4])
            plan.add_task("Write tests for core functionality", dependencies=[5])
            plan.add_task("Review and optimize the implementation", dependencies=[6])
        elif any(kw in desc_lower for kw in ["fix", "bug", "error", "issue"]):
            plan.add_task("Reproduce and understand the bug")
            plan.add_task("Identify the root cause")
            plan.add_task("Implement the fix", dependencies=[2])
            plan.add_task("Verify the fix resolves the issue", dependencies=[3])
            plan.add_task("Check for regressions", dependencies=[4])
        elif any(kw in desc_lower for kw in ["refactor", "improve", "optimize", "clean"]):
            plan.add_task("Analyze the current codebase")
            plan.add_task("Identify areas for improvement")
            plan.add_task("Plan the refactoring approach", dependencies=[2])
            plan.add_task("Implement changes incrementally", dependencies=[3])
            plan.add_task("Run tests to verify no regressions", dependencies=[4])
        elif any(kw in desc_lower for kw in ["explain", "how", "what", "why"]):
            plan.add_task("Read and analyze the relevant code")
            plan.add_task("Explain the code structure and logic")
            plan.add_task("Provide examples and usage guidance", dependencies=[2])
        else:
            plan.add_task("Understand the request")
            plan.add_task("Gather necessary information")
            plan.add_task("Formulate a response")
            plan.add_task("Provide the answer with examples", dependencies=[3])

        return plan
