import os
import subprocess

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
      "properties": { "command":  { "type": "string" } },
      "required": ["command"]
    }
  }
]

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
      if (block.type == "tool_use"):
        output = run_bash(block.input["command"])
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
      query = input("\033[36ms01 >> \033[0m")
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

