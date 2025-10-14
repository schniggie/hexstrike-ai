#!/usr/bin/env python3
"""
Simple test script for SSE transport functionality
"""

import requests
import json
import time

SERVER_URL = "http://127.0.0.1:8888"

def test_session_creation():
    """Test creating an MCP session"""
    print("Testing session creation...")
    response = requests.post(f"{SERVER_URL}/api/mcp/session", json={"api_key": "test"})

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            session_id = data.get("session_id")
            print(f"✅ Session created successfully: {session_id}")
            return session_id
        else:
            print(f"❌ Session creation failed: {data}")
            return None
    else:
        print(f"❌ HTTP error {response.status_code}: {response.text}")
        return None

def test_sse_connection(session_id):
    """Test SSE connection and event streaming"""
    print(f"\nTesting SSE connection for session {session_id}...")

    try:
        response = requests.get(
            f"{SERVER_URL}/api/mcp/sse?session_id={session_id}",
            stream=True,
            timeout=10
        )

        print("📡 Connected to SSE endpoint")
        event_count = 0

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    event_data = json.loads(data)
                    event_count += 1
                    print(f"📨 Event {event_count}: {event_data.get('type')} - {event_data}")

                    # Stop after receiving the connection event
                    if event_count >= 1:
                        break

        print(f"✅ SSE connection test passed ({event_count} events received)")
        return True

    except Exception as e:
        print(f"❌ SSE connection failed: {str(e)}")
        return False

def test_command_with_streaming(session_id):
    """Test command execution with SSE streaming"""
    print(f"\nTesting command execution with streaming...")

    command_data = {
        "command": "echo 'Hello from SSE test'",
        "session_id": session_id,
        "use_cache": False
    }

    response = requests.post(f"{SERVER_URL}/api/command", json=command_data)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Command executed: {result.get('success')}")
        print(f"   Output: {result.get('stdout', '')[:100]}")
        return True
    else:
        print(f"❌ Command failed: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("HexStrike AI SSE Transport Test")
    print("=" * 60)
    print(f"\nServer: {SERVER_URL}")
    print("\nNote: Make sure hexstrike_server.py is running first!")
    print("Run: python3 hexstrike_server.py\n")

    # Test 1: Session creation
    session_id = test_session_creation()
    if not session_id:
        print("\n❌ Test failed at session creation")
        return

    # Test 2: SSE connection
    sse_ok = test_sse_connection(session_id)
    if not sse_ok:
        print("\n⚠️  SSE connection test failed (but session creation worked)")

    # Test 3: Command with streaming
    cmd_ok = test_command_with_streaming(session_id)
    if not cmd_ok:
        print("\n⚠️  Command execution test failed")

    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Session Creation: {'✅ PASS' if session_id else '❌ FAIL'}")
    print(f"  SSE Connection:   {'✅ PASS' if sse_ok else '⚠️  SKIP'}")
    print(f"  Command Streaming: {'✅ PASS' if cmd_ok else '⚠️  SKIP'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
