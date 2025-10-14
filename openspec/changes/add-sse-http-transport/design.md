# Technical Design: SSE/HTTP Transport for HexStrike MCP

## Context

HexStrike AI currently uses FastMCP with stdio transport, where the MCP client (`hexstrike_mcp.py`) communicates with AI agents via standard input/output streams. The client then makes HTTP requests to the Flask API server (`hexstrike_server.py`) to execute security tools. This architecture limits deployment to same-machine scenarios and prevents real-time streaming of tool execution progress.

**Current Architecture:**
```
AI Agent (Claude) <--(stdio)--> hexstrike_mcp.py <--(HTTP REST)--> hexstrike_server.py (Flask API)
```

**Target Architecture:**
```
AI Agent (Claude) <--(SSE/HTTP)--> hexstrike_mcp.py <--(HTTP REST + SSE)--> hexstrike_server.py (Flask API)
```

### Stakeholders
- **AI Agent Users**: Security researchers, penetration testers, CTF players
- **HexStrike Developers**: Maintainers of the codebase
- **Enterprise Users**: Organizations deploying HexStrike remotely
- **MCP Client Developers**: Claude Desktop, VS Code Copilot, Cursor teams

### Constraints
- Must maintain backward compatibility with stdio transport
- Must support existing 150+ security tools without modification
- Must work with FastMCP 0.2.0+ framework
- Must handle long-running tools (5+ minutes) without timeout
- Must scale to 50+ concurrent AI agent connections
- Must deploy on Kali Linux 2024.1+ and Ubuntu 22.04 LTS

## Goals / Non-Goals

### Goals
- ✅ Enable remote access to HexStrike MCP server over network
- ✅ Implement real-time streaming for security tool output
- ✅ Support multiple concurrent AI agent sessions with isolation
- ✅ Add authentication/authorization for secure remote access
- ✅ Maintain 100% backward compatibility with stdio transport
- ✅ Deliver sub-200ms latency for streaming updates
- ✅ Support WebSocket, SSE, and long-polling transports

### Non-Goals
- ❌ WebSocket-based transport (use SSE for simplicity)
- ❌ GraphQL-based API (stick with REST + SSE)
- ❌ Multi-region deployment with load balancing (future v7.0)
- ❌ Browser-based web UI for HexStrike (focus on MCP protocol)
- ❌ Custom binary protocol (stick with JSON over HTTP/SSE)

## Decisions

### Decision 1: Use Server-Sent Events (SSE) for Streaming

**What:** Implement SSE for unidirectional streaming from server to client.

**Why:**
- **Simplicity**: SSE uses standard HTTP, no WebSocket complexity
- **Browser Support**: Works in all modern browsers without additional libraries
- **Automatic Reconnection**: Built-in reconnection with event ID tracking
- **Lightweight**: Lower overhead than WebSocket for one-way streaming
- **Firewall-Friendly**: Uses standard HTTP/HTTPS ports (80/443)

**Alternatives Considered:**
1. **WebSocket**: Bidirectional, but overkill for our use case (MCP requests go via HTTP POST, only responses need streaming)
2. **Long-Polling**: Works but less efficient than SSE for continuous updates
3. **gRPC Streaming**: Higher performance but adds complexity and requires protobuf

**Implementation:**
```python
# Server-side (hexstrike_server.py)
@app.route('/api/mcp/sse')
def mcp_sse_endpoint():
    def event_stream():
        session_id = request.args.get('session_id')
        queue = session_manager.get_queue(session_id)

        while True:
            message = queue.get()
            if message is None:  # Sentinel for disconnect
                break
            yield f"data: {json.dumps(message)}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

# Client-side (hexstrike_mcp.py)
class SSETransport:
    def __init__(self, server_url: str, session_id: str):
        self.sse_url = f"{server_url}/api/mcp/sse?session_id={session_id}"
        self.client = sseclient.SSEClient(self.sse_url)

    def listen(self):
        for event in self.client.events():
            self.handle_message(json.loads(event.data))
```

### Decision 2: Session-Based Authentication with API Keys

**What:** Use API key authentication with session tokens for stateful connections.

**Why:**
- **Security**: Prevents unauthorized access to security tools
- **Simplicity**: Easier to implement than OAuth2 for this use case
- **Flexibility**: Supports both long-lived API keys and short-lived session tokens
- **Auditability**: Each request is tied to an authenticated session

**Alternatives Considered:**
1. **OAuth2**: More secure but complex for command-line tool usage
2. **mTLS**: Very secure but difficult to set up and manage certificates
3. **No Authentication**: Unacceptable for remote deployments

**Implementation:**
```python
# API Key generation
import secrets
api_key = secrets.token_urlsafe(32)  # 256-bit random key

# Authentication middleware
@app.before_request
def authenticate_request():
    if request.endpoint in ['health', 'static']:
        return  # Skip auth for public endpoints

    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not api_key or not auth_manager.validate_key(api_key):
        abort(401, "Invalid or missing API key")

    # Create or retrieve session
    session_id = auth_manager.get_or_create_session(api_key)
    g.session_id = session_id
```

### Decision 3: Hybrid Transport Architecture

**What:** Support stdio, SSE, and HTTP transports with auto-detection.

**Why:**
- **Backward Compatibility**: Existing stdio clients continue to work
- **Flexibility**: Users choose the best transport for their deployment
- **Future-Proofing**: Easy to add new transports (WebSocket, gRPC) later

**Auto-Detection Logic:**
```python
def detect_transport(args):
    if args.transport:
        return args.transport  # Explicit flag takes precedence

    if args.server_url:
        return 'sse'  # Remote server implies SSE/HTTP

    if sys.stdin.isatty():
        return 'stdio'  # Interactive terminal implies stdio

    return 'stdio'  # Default to stdio for safety
```

### Decision 4: In-Memory Session Storage (Initial), Redis (Future)

**What:** Use in-memory dictionary for session storage in v6.1, migrate to Redis in v7.0.

**Why:**
- **Simplicity**: In-memory storage is sufficient for single-server deployments
- **Performance**: Sub-millisecond session lookups
- **Migration Path**: Easy to swap for Redis when scaling requirements increase

**Implementation (v6.1):**
```python
class SessionManager:
    def __init__(self):
        self.sessions = {}  # session_id -> Session object
        self.queues = {}    # session_id -> Queue for SSE events
        self.lock = threading.Lock()

    def create_session(self, api_key: str) -> str:
        session_id = secrets.token_urlsafe(16)
        with self.lock:
            self.sessions[session_id] = Session(session_id, api_key)
            self.queues[session_id] = queue.Queue()
        return session_id

    def cleanup_session(self, session_id: str):
        with self.lock:
            self.sessions.pop(session_id, None)
            q = self.queues.pop(session_id, None)
            if q:
                q.put(None)  # Signal SSE to close
```

**Future Migration (v7.0):**
```python
import redis
class RedisSessionManager:
    def __init__(self, redis_url: str):
        self.redis = redis.Redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
```

### Decision 5: Streaming Progress Protocol

**What:** Define JSON-RPC-like protocol for streaming progress updates.

**Why:**
- **Structure**: Well-defined message format for parsing
- **Extensibility**: Easy to add new message types
- **Compatibility**: Compatible with MCP protocol structure

**Message Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/progress",
  "params": {
    "tool": "nmap",
    "target": "192.168.1.0/24",
    "progress": 45.2,
    "phase": "Port scanning",
    "elapsed_seconds": 120,
    "estimated_remaining_seconds": 145,
    "partial_output": "Discovered open port 22/tcp on 192.168.1.10"
  }
}

{
  "jsonrpc": "2.0",
  "method": "tools/result",
  "params": {
    "tool": "nuclei",
    "target": "example.com",
    "vulnerability": {
      "template": "CVE-2023-1234",
      "severity": "high",
      "matched_at": "https://example.com/admin",
      "description": "SQL Injection vulnerability"
    }
  }
}
```

### Decision 6: FastMCP Integration Strategy

**What:** Extend FastMCP with custom transport layer while maintaining framework compatibility.

**Why:**
- **Framework Support**: FastMCP provides MCP protocol handling
- **Flexibility**: Custom transports allow SSE/HTTP without forking FastMCP
- **Maintenance**: Easier to upgrade FastMCP versions

**Implementation:**
```python
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

class HexStrikeMCP(FastMCP):
    def __init__(self, name: str, transport: str = 'stdio'):
        super().__init__(name)
        self.transport = transport
        self.session_manager = SessionManager()

    def run(self):
        if self.transport == 'stdio':
            # Use built-in stdio transport
            asyncio.run(stdio_server(self))
        elif self.transport == 'sse':
            # Use custom SSE transport
            self.run_sse_server()
        elif self.transport == 'http':
            # Use custom HTTP transport
            self.run_http_server()
```

## Risks / Trade-offs

### Risk 1: Increased Complexity
- **Risk**: Adding SSE/HTTP transport increases codebase complexity by ~30%
- **Mitigation**:
  - Maintain clear separation between transport layer and tool logic
  - Comprehensive unit tests for each transport type
  - Document transport architecture with diagrams
- **Trade-off**: Complexity vs. functionality (remote access is critical feature)

### Risk 2: Network Security Vulnerabilities
- **Risk**: Remote access exposes HexStrike server to network attacks
- **Mitigation**:
  - Mandatory authentication for all remote connections
  - Rate limiting to prevent DoS attacks
  - HTTPS/TLS encryption for production deployments
  - IP whitelisting for enterprise environments
- **Trade-off**: Security overhead vs. remote access convenience

### Risk 3: Session State Management
- **Risk**: In-memory sessions lost on server restart, breaking active connections
- **Mitigation**:
  - Document session persistence limitations
  - Implement graceful reconnection with checkpoint resume
  - Plan Redis migration for v7.0 with persistent sessions
- **Trade-off**: Simplicity (in-memory) vs. reliability (Redis)

### Risk 4: Streaming Performance Overhead
- **Risk**: SSE streaming may increase latency compared to direct HTTP responses
- **Mitigation**:
  - Benchmark SSE vs. HTTP latency (<200ms target)
  - Implement output buffering strategies (line vs. chunk)
  - Use HTTP/2 for multiplexing where available
- **Trade-off**: Real-time updates vs. total request throughput

### Risk 5: Backward Compatibility Maintenance
- **Risk**: Supporting 3 transports (stdio/SSE/HTTP) increases testing burden
- **Mitigation**:
  - Automated integration tests for all transport types
  - Deprecation warnings for future transport changes
  - Clear documentation on recommended transports per use case
- **Trade-off**: Flexibility vs. maintenance burden

## Migration Plan

### Phase 1: Initial Implementation (Weeks 1-2)
1. Implement SSE endpoint in Flask server
2. Create `SSETransport` class in MCP client
3. Add session management with in-memory storage
4. Implement basic authentication with API keys

### Phase 2: Streaming and Progress (Weeks 3-4)
5. Add streaming callbacks to tool execution functions
6. Implement progress tracking for nmap, nuclei, gobuster
7. Create real-time vulnerability streaming
8. Add reconnection and error recovery logic

### Phase 3: Testing and Documentation (Week 5)
9. Write integration tests for SSE/HTTP transports
10. Test concurrent connections (10+ agents)
11. Create setup guides and configuration examples
12. Document migration from stdio to SSE/HTTP

### Phase 4: Security Hardening (Week 6)
13. Implement HTTPS/TLS support
14. Add rate limiting and IP whitelisting
15. Implement audit logging
16. Security review and penetration testing

### Rollback Strategy
- If SSE/HTTP transport has critical issues:
  1. Disable SSE/HTTP via feature flag
  2. Revert to stdio-only mode
  3. Fix issues in separate branch
  4. Re-enable after validation

## Open Questions

1. **Q**: Should we support WebSocket transport in addition to SSE?
   - **A**: No for v6.1. SSE is sufficient for streaming responses. WebSocket can be added in v7.0 if needed.

2. **Q**: How should we handle API key rotation?
   - **A**: Initial implementation uses static keys. v6.2 will add key rotation with grace period (30 days).

3. **Q**: Should we implement request queueing for rate limiting?
   - **A**: Yes. Use Redis queue (or in-memory for v6.1) with configurable queue depth (default: 100 requests/session).

4. **Q**: How do we handle cross-origin requests for web-based MCP clients?
   - **A**: Implement CORS middleware with configurable allowed origins. Default: localhost only.

5. **Q**: Should we support HTTP/2 or HTTP/3 for improved performance?
   - **A**: HTTP/2 via ASGI server (Uvicorn) in v6.1. HTTP/3 deferred to v7.0+ based on adoption.

6. **Q**: How do we monitor SSE connection health?
   - **A**: Implement heartbeat messages every 30 seconds. Client reconnects if no heartbeat received for 60 seconds.

## Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| SSE Connection Latency | <500ms | Time from connection request to first event |
| Streaming Update Latency | <200ms | Time from output generated to event delivered |
| Concurrent Connections | 50+ | Load testing with 50 simultaneous agents |
| Memory per Session | <10MB | Measure with 50 active sessions |
| Reconnection Time | <2s | Time from disconnect to resumed streaming |
| API Key Validation | <10ms | Benchmark with 1000 validation requests |

## Dependencies

### New Python Packages
- `sse-starlette` (0.10.0+) - SSE support for async frameworks
- `python-jose` (3.3.0+) - JWT token generation/validation
- `redis` (5.0.0+) - Session storage (future, optional for v6.1)

### Infrastructure
- **Development**: No changes (localhost deployment)
- **Production**: Reverse proxy (nginx) for TLS termination, load balancing

### External Services
- **Optional**: Redis for persistent session storage (v7.0)
- **Optional**: Prometheus for metrics collection
- **Optional**: Datadog/Grafana for monitoring dashboards
