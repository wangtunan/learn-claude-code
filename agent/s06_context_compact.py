#!/usr/bin/env python3
"""Agent with todo management for tracking multi-step tasks."""

import os
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv(override=True)

client = Anthropic(
    base_url=os.environ["ANTHROPIC_BASE_URL"],
)

WORKDIR = Path.cwd()
SYSTEM =  f"""You are a coding agent at {WORKDIR}. Use tools to solve tasks."""
THRESHOLD = 50000
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
KEEP_RECENT = 3
PRESERVE_RESULT_TOOLS  = { "read_file" }


TOOLS  = [
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
        "name": "load_skill",
        "description": "Load specialized knowledge by name",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": { "type": "string", "description": "Skill name to load" }
            }
        },
        "required": ["name"]
    },
    {
        "name": "compact",
        "description": "Trigger manual conversation compression.",
        "input_schema": {
            "type": "object",
            "properties": {
                "focus": { "type": "string", "description": "What to preserve in the summary" }
            }
        },
        "required": ["focus"]
    },
]


TOOLS_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "compact":    lambda **kw: "Manual compression requested.",
}

def estimate_tokens(messages: list) -> int:
    """Rough token count: ~4 chars per token."""
    return len(str(messages)) // 4

def micro_compact(messages: list) -> list:
    # Collect tool results
    tool_results = []
    for msg_idx, msg in enumerate(messages):
        if msg["role"] == "user" and isinstance(msg.get("content"), list):
            for part_idx, part in enumerate(msg["content"]):
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    tool_results.append((msg_idx, part_idx, part))
    
    if len(tool_results) > KEEP_RECENT:
        return messages

    # Find tool_name for each results
    tool_name_map = {}
    for msg in messages:
        if msg["role"] == "assistant":
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if hasattr(block, "type") and block.type == "tool_use":
                        tool_name_map["block_id"] = block.name
    
    # Clear old tool results
    to_clear = tool_results[:-KEEP_RECENT]
    for _, _, result in to_clear:
        if not isinstance(result.get("content"), str) or len(result["content"]) <= 100:
            continue
        tool_id = result.get("tool_use_id", "")
        tool_name = tool_name_map.get(tool_id, "unknown")
        if tool_name in PRESERVE_RESULT_TOOLS:
            continue
        result["content"] = f"[Previous: used {tool_name}]"
    return messages

def auto_compact(messages: list) -> list:
    # Save transcript
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str) + "\n")
    print(f"[transcript saved: {transcript_path}]")

    # Ask LLM to summarize
    conversation_text = json.dumps(messages, default=str)[-80000:]
    response = client.messages.create(
        model = os.getenv("MODEL_ID"),
        messages=[{
            "role": "user",
            "content": f"""
                Summarize this conversation for continuity. Include:
                1) What was accomplished, 2) Current state, 3) Key decisions made.
                Be concise but preserve critical details.\n\n {conversation_text}
            """,
            
        }],
        max_tokens=2000
    )
    summary = next((block.text for block in response.content if hasattr(block, "text")), "")
    if not summary:
        summary = "No summary generated."

    return [
        {"role": "user", "content": f"[Conversation compressed. Transcript: {transcript_path}]\n\n{summary}"},
    ]


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

def agent_loop(messages: List[Dict[str, Any]]):
    
    while True:
        micro_compact(messages)

        if estimate_tokens(messages) > THRESHOLD:
            print("[auto_compact triggered]")
            messages[:] = auto_compact(messages)

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
        manual_compact = False

        for block in response.content:
            if block.type == "tool_use":
                if block.name == "compact":
                    manual_compact = True
                    output = "Compressing..."
                else:
                    handler = TOOLS_HANDLERS.get(block.name)
                    try:
                        output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                    except Exception as e:
                        output = f"Error: {e}"

                print(f"> {block.name}:")
                print(str(output)[:200])

                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output),
                })

        # Add tool results to messages
        messages.append({"role": "user", "content": results})

        if manual_compact:
            print("[manual compact]")
            messages[:] = auto_compact(messages)
            return


def main() -> None:
    """Main function to run the agent loop interactively."""
    history = []

    while True:
        try:
            query = input("\033[36ms06 >> \033[0m")
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