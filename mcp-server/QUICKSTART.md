# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

### Step 2: Test the Server
```bash
# Test with Python directly
python utility_server.py

# In another terminal, test with:
python test_server.py
```

### Step 3: Register with Claude Desktop

1. Create or edit `~/.claude/mcp.json`
2. Add this configuration (update the path):

```json
{
  "mcpServers": {
    "utility-server": {
      "command": "python3",
      "args": ["/e/person/learn-claude-code/mcp-server/utility_server.py"]
    }
  }
}
```

3. Restart Claude Desktop

### Step 4: Start Using with Claude

Now you can ask Claude things like:
- "Read the README file"
- "List files in the current directory"
- "What's 20¡ãC in Fahrenheit?"
- "Calculate 15 * (3 + 7) / 2"

## Common Issues & Solutions

### "Command not found: python3"
- Use full path: `"command": "/usr/bin/python3"`
- Or use: `"command": "python"` if that's your Python command

### Server won't start
- Check Python version: `python3 --version` (needs 3.8+)
- Install dependencies: `pip install mcp psutil`
- Check file permissions: `chmod +x utility_server.py`

### Claude doesn't see the tools
- Restart Claude Desktop after editing mcp.json
- Check Claude logs for errors
- Test server manually: `python utility_server.py`

## Next Steps

### Extend the Server
Add your own tools by editing `utility_server.py`:

```python
@server.tool()
async def my_custom_tool(param: str) -> str:
    """Description of your tool."""
    return f"Processed: {param}"
```

### Create Specialized Servers
- Weather server with API integration
- Database query server
- Email notification server
- File processing server

### Learn More
- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Claude Desktop Documentation](https://docs.anthropic.com/claude/docs/claude-desktop)