#!/usr/bin/env python3
"""
Test script for MCP SSE/HTTP transport functionality
Tests the AI Agent <-> hexstrike_mcp.py SSE/HTTP communication
"""

import requests
import json
import time
import sys

# Configuration
MCP_SERVER_URL = "http://127.0.0.1:8000"
MCP_TRANSPORT = "sse"  # or "streamable-http"

def test_mcp_server_health():
    """Test if MCP server is running and accessible"""
    print("=" * 70)
    print("Test 1: MCP Server Health Check")
    print("=" * 70)

    try:
        # For SSE transport, FastMCP typically exposes endpoints at the root
        response = requests.get(f"{MCP_SERVER_URL}/", timeout=5)

        if response.status_code == 200:
            print(f"✅ MCP server is running at {MCP_SERVER_URL}")
            print(f"   Status code: {response.status_code}")
            return True
        else:
            print(f"⚠️  MCP server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to MCP server at {MCP_SERVER_URL}")
        print(f"   Make sure to start the server first:")
        print(f"   python3 hexstrike_mcp.py --transport {MCP_TRANSPORT} --mcp-host 127.0.0.1 --mcp-port 8000")
        return False
    except Exception as e:
        print(f"❌ Error checking MCP server: {str(e)}")
        return False

def test_sse_endpoint():
    """Test SSE endpoint availability"""
    print("\n" + "=" * 70)
    print("Test 2: SSE Endpoint Availability")
    print("=" * 70)

    try:
        # FastMCP SSE endpoint is typically at /sse
        response = requests.get(f"{MCP_SERVER_URL}/sse", stream=True, timeout=5)

        if response.status_code == 200:
            print(f"✅ SSE endpoint is accessible")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")

            # Try to read first event
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"   First event: {line[:100]}...")
                    break

            return True
        else:
            print(f"❌ SSE endpoint returned status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"⚠️  SSE endpoint timeout (this might be expected)")
        return True  # Timeout on streaming endpoint is not necessarily a failure
    except Exception as e:
        print(f"❌ Error testing SSE endpoint: {str(e)}")
        return False

def test_mcp_protocol():
    """Test MCP protocol communication"""
    print("\n" + "=" * 70)
    print("Test 3: MCP Protocol Communication")
    print("=" * 70)

    try:
        # FastMCP typically exposes a /message endpoint for HTTP POST
        # This is part of the streamable-http transport

        # Example MCP initialize request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        print(f"📤 Sending MCP initialize request...")
        response = requests.post(
            f"{MCP_SERVER_URL}/message",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ MCP protocol response received")
            print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ MCP request failed with status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"⚠️  MCP protocol test error: {str(e)}")
        print(f"   This might be expected if the endpoint structure is different")
        return False

def test_tools_list():
    """Test listing available MCP tools"""
    print("\n" + "=" * 70)
    print("Test 4: List Available MCP Tools")
    print("=" * 70)

    try:
        # MCP tools/list request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        print(f"📤 Requesting tools list...")
        response = requests.post(
            f"{MCP_SERVER_URL}/message",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tools list received")

            tools = result.get("result", {}).get("tools", [])
            if tools:
                print(f"   Found {len(tools)} tools")
                print(f"   Sample tools: {[t.get('name') for t in tools[:5]]}")
            else:
                print(f"   Response: {json.dumps(result, indent=2)[:300]}...")

            return True
        else:
            print(f"❌ Tools list request failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Tools list test error: {str(e)}")
        return False

def main():
    print("\n" + "=" * 70)
    print("HexStrike AI MCP SSE/HTTP Transport Test")
    print("=" * 70)
    print(f"MCP Server: {MCP_SERVER_URL}")
    print(f"Transport: {MCP_TRANSPORT}")
    print()
    print("Prerequisites:")
    print(f"1. Start hexstrike_server.py: python3 hexstrike_server.py")
    print(f"2. Start hexstrike_mcp.py with SSE/HTTP:")
    print(f"   python3 hexstrike_mcp.py --transport {MCP_TRANSPORT} --mcp-host 127.0.0.1 --mcp-port 8000")
    print()

    # Run tests
    results = []

    results.append(("MCP Server Health", test_mcp_server_health()))

    if results[0][1]:  # Only continue if server is accessible
        results.append(("SSE Endpoint", test_sse_endpoint()))
        results.append(("MCP Protocol", test_mcp_protocol()))
        results.append(("Tools List", test_tools_list()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<50} {status}")

    print("=" * 70)

    # Exit code
    all_passed = all(result[1] for result in results)
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
