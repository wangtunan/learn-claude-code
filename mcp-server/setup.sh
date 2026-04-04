#!/bin/bash
# Setup script for Utility MCP Server

echo "Setting up Utility MCP Server..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Installation complete!"
echo ""
echo "To test the server:"
echo "  python utility_server.py"
echo ""
echo "To register with Claude Desktop, add to ~/.claude/mcp.json:"
echo '{
  "mcpServers": {
    "utility-server": {
      "command": "python3",
      "args": ["/full/path/to/utility_server.py"]
    }
  }
}'