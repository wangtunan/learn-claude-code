import os
import subprocess

from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv(override=True)

client = Anthropic(
  base_url=os.environ["ANTHROPIC_BASE_URL"],
)

WORKDIR = Path.cwd()
SYSTEM = f"You are a code agent at {WORKDIR}. Use bash to resolve tasks. Act, don't explain."

TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
]

TOOLS_HANDLERS = {
  "bash": lambda **kw: run_bash(kw["command"]),
  "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
  "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
  "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"])
}

def safe_path(p: str) -> Path:
  path = (WORKDIR / p).resolve()
  if not path.is_relative_to(WORKDIR):
    raise ValueError(f"Path escapes workspace: {p}")
  return path

def run_bash(command: str) -> str:
  dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
  if any(d in command for d in dangerous):
      return "Error: Dangerous command blocked"
  try:
      r = subprocess.run(
        command,
        shell=True,
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="replace",
      )
      out = ((r.stdout or "") + (r.stderr or "")).strip()
      return out[:50000] if out else "(no output)"
  except subprocess.TimeoutExpired:
      return "Error: Timeout (120s)"
  except (FileNotFoundError, OSError) as e:
      return f"Error: {e}"

def run_read(path: str, limit: int | None = None) -> str:
  try:
    text = safe_path(path).read_text()
    lines = text.splitlines()

    if limit and limit < len(lines):
      lines = lines[:limit] + [f"...({len(lines) - limit} more lines)"]
    
    return "\n".join(lines)[:50000]
  except Exception as e:
    return f"Error: {e}"

def run_write(path: str, content: str) -> str:
  try:
    fp = safe_path(path)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content)

    return f"Wrote {len(content)} bytes to {path}"
  except Exception as e:
    return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
  try:
    fp = safe_path(path)
    content = fp.read_text()

    if old_text not in content:
      return f"Error: '{old_text}' not found in {path}"
    
    fp.write_text(content.replace(old_text, new_text, 1))
    return f"Edited {path}"
  except Exception as e:
    return f"Error: {e}"

def agent_loop(messages: list):
  while True:
    response = client.messages.create(
      model=os.environ["MODEL_ID"],
      messages=messages,
      system=SYSTEM,
      tools=TOOLS,
      max_tokens=8000
    )

    # assistant
    messages.append({ "role": "assistant", "content": response.content })

    # done
    if response.stop_reason != "tool_use":
      return
    
    # call
    results = []
    for block in response.content:
      if block.type == "tool_use":
        handler = TOOLS_HANDLERS.get(block.name)
        output = handler(**block.input) if handler else f"Error: Unknown tool: {block.name}"
        results.append({
          "type": "tool_result",
          "tool_use_id": block.id,
          "content": output
        })
    
    messages.append({ "role": "user", "content": results })

if __name__ == "__main__":
  history = []

  while True:
    try:
      query = input("\033[36ms02 >> \033[0m")
    except (EOFError, KeyboardInterrupt):
      break;
    
    if query.lower() in ["exit", "q", "quit"]:
      break;
    
    history.append({ "role": "user", "content": query })
    agent_loop(history);
    response_content = history[-1]["content"]

    if isinstance(response_content, list):
      for block in response_content:
        if hasattr(block, "text"):
          print(block.text)
    
    print()

