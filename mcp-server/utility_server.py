#!/usr/bin/env python3
"""utility_server.py - A versatile MCP server with useful tools"""

import asyncio
import json
import os
import sys
import math
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

# Create server instance
server = Server("utility-server", version="1.0.0")

# ========== File Operations ==========

@server.tool()
async def read_file(filepath: str) -> str:
    """Read the contents of a file.
    
    Args:
        filepath: Path to the file to read
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File '{filepath}' does not exist"
        
        if not path.is_file():
            return f"Error: '{filepath}' is not a file"
            
        content = path.read_text(encoding='utf-8')
        return f"File '{filepath}' contents:\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@server.tool()
async def list_directory(directory: str = ".") -> str:
    """List files and directories in a given path.
    
    Args:
        directory: Directory path to list (default: current directory)
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        items = []
        for item in path.iterdir():
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            size = item.stat().st_size if item.is_file() else 0
            items.append(f"{item_type} {item.name} ({size} bytes)")
        
        if not items:
            return f"Directory '{directory}' is empty"
        
        return f"Contents of '{directory}':\n\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@server.tool()
async def file_info(filepath: str) -> str:
    """Get information about a file or directory.
    
    Args:
        filepath: Path to check
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: '{filepath}' does not exist"
        
        stats = path.stat()
        info = {
            "Path": str(path.absolute()),
            "Type": "Directory" if path.is_dir() else "File",
            "Size": f"{stats.st_size} bytes",
            "Created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "Modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "Permissions": oct(stats.st_mode)[-3:],
        }
        
        result = f"File information for '{filepath}':\n"
        for key, value in info.items():
            result += f"  {key}: {value}\n"
        
        return result
    except Exception as e:
        return f"Error getting file info: {str(e)}"

# ========== Calculator Tools ==========

@server.tool()
async def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
    """
    try:
        # Basic safety check
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        # Use eval with limited globals for safety
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

@server.tool()
async def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units.
    
    Args:
        value: Value to convert
        from_unit: Source unit (e.g., "km", "miles", "celsius", "fahrenheit")
        to_unit: Target unit
    """
    try:
        # Temperature conversions
        if from_unit.lower() in ["c", "celsius"] and to_unit.lower() in ["f", "fahrenheit"]:
            result = (value * 9/5) + 32
            return f"{value}¡ãC = {result:.2f}¡ãF"
        
        elif from_unit.lower() in ["f", "fahrenheit"] and to_unit.lower() in ["c", "celsius"]:
            result = (value - 32) * 5/9
            return f"{value}¡ãF = {result:.2f}¡ãC"
        
        # Distance conversions
        elif from_unit.lower() in ["km", "kilometers"] and to_unit.lower() in ["miles"]:
            result = value * 0.621371
            return f"{value} km = {result:.2f} miles"
        
        elif from_unit.lower() in ["miles"] and to_unit.lower() in ["km", "kilometers"]:
            result = value * 1.60934
            return f"{value} miles = {result:.2f} km"
        
        else:
            return f"Error: Unsupported conversion from '{from_unit}' to '{to_unit}'"
    except Exception as e:
        return f"Error converting units: {str(e)}"

# ========== System Information ==========

@server.tool()
async def system_info() -> str:
    """Get information about the current system."""
    try:
        import platform
        import psutil
        
        info = {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Python Version": platform.python_version(),
            "CPU Count": psutil.cpu_count(),
            "Memory Total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "Memory Available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "Current Directory": os.getcwd(),
        }
        
        result = "System Information:\n"
        for key, value in info.items():
            result += f"  {key}: {value}\n"
        
        return result
    except ImportError:
        return "Note: Install 'psutil' package for detailed system information"
    except Exception as e:
        return f"Error getting system info: {str(e)}"

@server.tool()
async def current_time(timezone: str = "local") -> str:
    """Get the current date and time.
    
    Args:
        timezone: Timezone (default: "local")
    """
    try:
        now = datetime.now()
        if timezone.lower() == "utc":
            from datetime import timezone as tz
            now = datetime.now(tz.utc)
        
        return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        return f"Error getting time: {str(e)}"

# ========== Text Processing ==========

@server.tool()
async def text_stats(text: str) -> str:
    """Get statistics about a text.
    
    Args:
        text: Text to analyze
    """
    try:
        words = text.split()
        chars = len(text)
        lines = text.count('\n') + 1 if text else 0
        
        stats = {
            "Characters": chars,
            "Words": len(words),
            "Lines": lines,
            "Average word length": f"{sum(len(w) for w in words)/len(words):.1f}" if words else "0",
            "Character count (no spaces)": len(text.replace(' ', '')),
        }
        
        result = "Text Statistics:\n"
        for key, value in stats.items():
            result += f"  {key}: {value}\n"
        
        return result
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

@server.tool()
async def format_json(json_string: str) -> str:
    """Format and validate a JSON string.
    
    Args:
        json_string: JSON string to format
    """
    try:
        parsed = json.loads(json_string)
        formatted = json.dumps(parsed, indent=2)
        return f"Formatted JSON:\n\n{formatted}"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"
    except Exception as e:
        return f"Error formatting JSON: {str(e)}"

# ========== Resources ==========

@server.resource("file://{path}")
async def read_file_resource(path: str) -> str:
    """Read a file as a resource."""
    try:
        return Path(path).read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading file: {str(e)}"

@server.resource("system://info")
async def system_info_resource() -> str:
    """Get system information as a resource."""
    try:
        import platform
        return f"System: {platform.system()}\nPython: {platform.python_version()}\nCWD: {os.getcwd()}"
    except Exception as e:
        return f"Error: {str(e)}"

# ========== Main Server Loop ==========

async def main():
    """Run the MCP server."""
    print("Starting Utility MCP Server...", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    # Check for required packages
    try:
        import mcp
    except ImportError:
        print("Error: MCP package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)
    
    asyncio.run(main())