#!/usr/bin/env python3
"""Test script for the Utility MCP Server"""

import subprocess
import json
import time
import sys
from pathlib import Path

def test_mcp_server():
    """Test the MCP server by sending JSON-RPC messages."""
    
    # Start the server as a subprocess
    print("Starting MCP server...")
    server_process = subprocess.Popen(
        [sys.executable, "utility_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give server time to start
    time.sleep(1)
    
    def send_request(method, params=None, request_id=1):
        """Send a JSON-RPC request to the server."""
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        print(f"Sending: {request_json.strip()}")
        
        server_process.stdin.write(request_json)
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print(f"Received: {json.dumps(response, indent=2)}")
            return response
        return None
    
    try:
        # Test 1: List available tools
        print("\n=== Test 1: Listing tools ===")
        response = send_request("tools/list")
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"\nAvailable tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
        # Test 2: Get server info
        print("\n=== Test 2: Server initialization ===")
        response = send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }, request_id=2)
        
        # Test 3: Try a simple tool call
        print("\n=== Test 3: Testing current_time tool ===")
        response = send_request("tools/call", {
            "name": "current_time",
            "arguments": {"timezone": "local"}
        }, request_id=3)
        
    finally:
        # Clean up
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        
        # Print any stderr output
        stderr_output = server_process.stderr.read()
        if stderr_output:
            print(f"\nServer stderr:\n{stderr_output}")

def test_tools_directly():
    """Test tools by importing and calling them directly."""
    print("\n=== Direct tool testing ===")
    
    # Add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        # Import the server module
        import utility_server
        
        # Create a simple test
        print("Testing calculate tool...")
        result = asyncio.run(utility_server.calculate("2 + 3 * 4"))
        print(f"2 + 3 * 4 = {result}")
        
        print("\nTesting convert_units tool...")
        result = asyncio.run(utility_server.convert_units(25, "celsius", "fahrenheit"))
        print(f"25°„C = {result}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure to run from the correct directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Utility MCP Server Test")
    print("=" * 50)
    
    # Check if asyncio is available for direct testing
    try:
        import asyncio
        test_tools_directly()
    except ImportError:
        print("asyncio not available for direct testing")
    
    # Run MCP protocol test
    test_mcp_server()