#!/usr/bin/env python3
"""Agent loop implementation for interacting with Anthropic API."""

import os
import subprocess
from typing import List, Dict, Any, Optional

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv(override=True)

client = Anthropic(
    base_url=os.environ["ANTHROPIC_BASE_URL"],
)

SYSTEM = f"You are a code agent at {os.getcwd()}. Use bash to resolve tasks. Act, don't explain."

TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    }
]


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


def agent_loop(messages: List[Dict[str, Any]]) -> None:
    """
    Run the agent loop to process messages with tool calls.

    Args:
        messages: List of message dictionaries.
    """
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
        for block in response.content:
            if block.type == "tool_use":
                output = run_bash(block.input["command"])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

        # Add tool results to messages
        messages.append({"role": "user", "content": results})


def main() -> None:
    """Main function to run the agent loop interactively."""
    history = []

    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
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