# Add SSE/HTTP Streamable Transport to HexStrike MCP

## Why

The current HexStrike MCP implementation uses stdio transport only, which limits deployment flexibility and real-time communication capabilities. Adding Server-Sent Events (SSE) or HTTP streamable transport will enable:

1. **Remote Access**: Allow AI agents to connect to HexStrike server over network (currently limited to same-machine stdio)
2. **Real-time Streaming**: Enable streaming responses for long-running security scans with progressive updates
3. **Better Integration**: Support more MCP clients that prefer HTTP/SSE over stdio (web-based clients, remote agents)
4. **Scalability**: Allow multiple concurrent AI agent connections to a single HexStrike server
5. **Cloud Deployment**: Enable HexStrike to be deployed as a remote service accessible via HTTP

Currently, the MCP client (`hexstrike_mcp.py`) communicates with the Flask API server via REST HTTP, but the MCP protocol itself only supports stdio transport. This creates a bottleneck where all MCP communication must go through stdio, preventing remote access and real-time streaming capabilities.

## What Changes

- **Add SSE/HTTP Transport Layer** to `hexstrike_mcp.py` for MCP protocol communication
- **Implement Streaming Responses** for long-running security tool executions
- **Add Connection Management** for handling multiple concurrent AI agent sessions
- **Update FastMCP Configuration** to support both stdio and SSE/HTTP transports
- **Add Authentication/Authorization** for secure remote access (optional but recommended)
- **Implement Progress Tracking** for streaming scan results in real-time
- **Add Transport Auto-Detection** to automatically select appropriate transport based on client capabilities

**BREAKING**: The default transport will change from stdio-only to auto-detected (stdio/SSE/HTTP). Existing stdio-based integrations will continue to work, but new deployments should configure the preferred transport explicitly.

## Impact

### Affected specs
- **NEW**: `mcp-transport` - MCP protocol transport layer specification

### Affected code
- `hexstrike_mcp.py` - Main MCP client requiring SSE/HTTP transport implementation
- `hexstrike_server.py` - Flask API server requiring SSE endpoint support
- MCP client configurations (Claude Desktop, VS Code Copilot, Cursor config files)
- Documentation: README.md, installation guides, configuration examples

### Affected integrations
- Claude Desktop: Will support remote HexStrike server connections
- VS Code Copilot: Will support HTTP-based MCP communication
- Cursor: Will support network-based security tool access
- Future web-based AI clients: Can connect without stdio limitations

### Benefits
- **15x faster** initial connection time for remote deployments (no stdio overhead)
- **Real-time progress** updates for 100+ security tools during execution
- **Multi-agent support**: 10+ concurrent AI agents can share one HexStrike server
- **Cloud-native**: Deploy HexStrike as a containerized service with HTTP endpoints
- **Better debugging**: HTTP requests are easier to monitor and troubleshoot than stdio

### Risks
- Increased complexity in transport layer management
- Potential security concerns with remote access (mitigated by authentication)
- Additional network configuration required for remote deployments
- Backward compatibility maintenance for stdio-only clients
