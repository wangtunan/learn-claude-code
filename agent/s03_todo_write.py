#!/usr/bin/env python3
"""Agent with todo management for tracking multi-step tasks."""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv(override=True)

client = Anthropic(
    base_url=os.environ["ANTHROPIC_BASE_URL"],
)

WORKDIR = Path.cwd()
SYSTEM = f"""
You are a code agent at {WORKDIR}.
Use the todo tool to plan multi-step tasks.
Mark in_progress before starting, completed when done.
Prefer tools over prose.
"""


class TodoManager:
    """Manager for tracking todo items."""

    def __init__(self) -> None:
        """Initialize TodoManager with empty items list."""
        self.items: List[Dict[str, str]] = []

    def update(self, items: List[Dict[str, str]]) -> str:
        """
        Update todo items with validation.

        Args:
            items: List of todo item dictionaries.

        Returns:
            Rendered todo list as string.

        Raises:
            ValueError: If validation fails.
        """
        if len(items) > 20:
            raise ValueError("Max 20 todos allowed")

        validated = []
        in_progress_count = 0

        for i, item in enumerate(items):
            text = str(item.get("text", "")).strip()
            status = str(item.get("status", "pending")).lower()
            item_id = str(item.get("id", str(i + 1)))

            if not text:
                raise ValueError(f"Item {item_id}: text required")
            if status not in ["pending", "completed", "in_progress"]:
                raise ValueError(f"Item {item_id}: invalid status '{status}'")
            if status == "in_progress":
                in_progress_count += 1

            validated.append({
                "id": item_id,
                "text": text,
                "status": status,
            })

        if in_progress_count > 1:
            raise ValueError("Only one in_progress todo allowed")

        self.items = validated
        return self.render()

    def render(self) -> str:
        """
        Render todo list as formatted string.

        Returns:
            Formatted todo list.
        """
        if not self.items:
            return "No todos."

        lines = []
        for item in self.items:
            marker = {
                "pending": "[]",
                "in_progress": "[>]",
                "completed": "[x]",
            }[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['text']}")

        done = sum(1 for t in self.items if t["status"] == "completed")
        lines.append(f"\n({done}/{len(self.items)}) completed")
        return "\n".join(lines)


TODO = TodoManager()

TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read file contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "name": "todo",
        "description": "Update task list. Track progress on multi-step tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "text": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                            },
                        },
                        "required": ["id", "text", "status"],
                    },
                },
            },
            "required": ["items"],
        },
    },
]

TOOLS_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "todo": lambda **kw: TODO.update(kw["items"]),
}


def safe_path(path_str: str) -> Path:
    """
    Convert a path string to a safe Path object within workspace.

    Args:
        path_str: Path string.

    Returns:
        Safe Path object.

    Raises:
        ValueError: If path escapes workspace.
    """
    path = (WORKDIR / path_str).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {path_str}")
    return path


def run_bash(command: str) -> str:
    """
    Execute a bash command safely.

    Args:
        command: The bash command to execute.

    Returns:
        The command output or error message.
    """
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        return output[:50000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def run_read(path: str, limit: Optional[int] = None) -> str:
    """
    Read file contents with optional line limit.

    Args:
        path: File path to read.
        limit: Maximum number of lines to return.

    Returns:
        File contents or error message.
    """
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()

        if limit and limit < len(lines):
            lines = lines[:limit] + [f"...({len(lines) - limit} more lines)"]

        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        path: File path to write.
        content: Content to write.

    Returns:
        Success message or error.
    """
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    """
    Replace exact text in a file.

    Args:
        path: File path to edit.
        old_text: Text to replace.
        new_text: New text.

    Returns:
        Success message or error.
    """
    try:
        file_path = safe_path(path)
        content = file_path.read_text()

        if old_text not in content:
            return f"Error: '{old_text}' not found in {path}"

        file_path.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


def agent_loop(messages: List[Dict[str, Any]]) -> None:
    """
    Run the agent loop to process messages with tool calls.

    Args:
        messages: List of message dictionaries.
    """
    rounds_since_todo = 0
    used_todo = False

    while True:
        response = client.messages.create(
            model=os.environ["MODEL_ID"],
            messages=messages,
            system=SYSTEM,
            tools=TOOLS,
            max_tokens=8000,
        )

        # Add assistant response to messages
        messages.append({"role": "assistant", "content": response.content})

        # Done if no tool use
        if response.stop_reason != "tool_use":
            return

        # Call tools
        results = []
        used_todo = False

        for block in response.content:
            if block.type == "tool_use":
                handler = TOOLS_HANDLERS.get(block.name)
                try:
                    output = (
                        handler(**block.input)
                        if handler
                        else f"Error: Unknown tool: {block.name}"
                    )
                except Exception as e:
                    output = f"Error: {e}"

                print(f"> {block.name}:")
                print(str(output)[:200])

                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output),
                })

                if block.name == "todo":
                    used_todo = True

        # Track todo usage for reminders
        rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
        if rounds_since_todo >= 3:
            results.append({
                "type": "text",
                "text": "<reminder>Update your todos.</reminder>",
            })

        # Add tool results to messages
        messages.append({"role": "user", "content": results})


def main() -> None:
    """Main function to run the agent loop interactively."""
    history = []

    while True:
        try:
            query = input("\033[36ms03 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break

        if query.lower() in ["exit", "q", "quit"]:
            break

        history.append({"role": "user", "content": query})
        agent_loop(history)
        response_content = history[-1]["content"]

        if isinstance(response_content, list):
            for block in response_content:
                if hasattr(block, "text"):
                    print(block.text)

        print()


if __name__ == "__main__":
    main()