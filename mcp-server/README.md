# Utility MCP Server

A versatile MCP (Model Context Protocol) server with useful tools for Claude.

## Features

### File Operations
- **read_file**: Read contents of any file
- **list_directory**: List files and directories
- **file_info**: Get detailed file information

### Calculator Tools
- **calculate**: Evaluate mathematical expressions
- **convert_units**: Convert between temperature and distance units

### System Information
- **system_info**: Get detailed system information (requires psutil)
- **current_time**: Get current date and time

### Text Processing
- **text_stats**: Analyze text statistics
- **format_json**: Format and validate JSON

### Resources
- **file://{path}**: Read files as resources
- **system://info**: Get system info as a resource

## Installation

### Quick Setup
```bash
# Run setup script
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install mcp psutil
```

## Usage

### Test the Server
```bash
python utility_server.py
```

### Register with Claude Desktop

Add to `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "utility-server": {
      "command": "python3",
      "args": ["/full/path/to/utility_server.py"]
    }
  }
}
```

### Test with MCP Inspector
```bash
npx @anthropics/mcp-inspector python3 utility_server.py
```

## Examples

Once registered with Claude, you can use commands like:

- "Read the README file"
- "List files in the current directory"
- "What's 25¡ãC in Fahrenheit?"
- "Calculate 15 * (3 + 7)"
- "Get system information"
- "Analyze this text: [your text here]"

## Security Notes

- File operations are limited to the server's environment
- Mathematical expressions are evaluated with restricted globals
- Always validate paths and inputs in production

## Extending the Server

To add new tools, follow this pattern:

```python
@server.tool()
async def my_tool(param1: str, param2: int) -> str:
    """Description of what the tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    """
    # Your implementation here
    return "Result"
```

## License

MIT