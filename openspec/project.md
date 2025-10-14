# Project Context

## Purpose
HexStrike AI MCP Agents v6.0 is an advanced AI-powered penetration testing and cybersecurity automation platform. The project provides autonomous AI agents with access to 150+ professional security tools through the Model Context Protocol (MCP), enabling intelligent security assessments, vulnerability discovery, CTF solving, bug bounty hunting, and red team operations.

**Core Goals:**
- Provide AI agents with comprehensive security testing capabilities via MCP
- Automate penetration testing workflows with intelligent decision-making
- Enable autonomous vulnerability discovery and exploit development
- Support bug bounty, CTF, and red team operations
- Deliver real-time visual feedback and vulnerability intelligence

## Tech Stack

### Primary Technologies
- **Python 3.8+** - Core application language
- **FastMCP** - MCP framework for AI agent communication
- **Flask** - Web framework for REST API server
- **Selenium** - Browser automation for web security testing
- **BeautifulSoup4** - HTML parsing and web scraping
- **aiohttp** - Async HTTP client for concurrent operations
- **mitmproxy** - HTTP/HTTPS proxy for traffic analysis
- **psutil** - System and process management

### Binary Analysis Libraries (Conditional)
- **pwntools** - Binary exploitation framework
- **angr** - Binary analysis and symbolic execution

### External Security Tools (150+)
The platform integrates with 150+ external security tools that must be installed separately:
- **Network & Reconnaissance**: nmap, masscan, rustscan, autorecon, amass, subfinder, fierce, dnsenum, theharvester, responder, netexec, enum4linux-ng
- **Web Application Security**: gobuster, feroxbuster, ffuf, nuclei, nikto, sqlmap, wpscan, arjun, paramspider, dalfox, httpx, katana, hakrawler
- **Authentication & Password**: hydra, john, hashcat, medusa, patator, evil-winrm, hash-identifier
- **Binary Analysis**: ghidra, radare2, gdb, binwalk, checksec, volatility3, foremost, steghide
- **Cloud & Container Security**: prowler, scout-suite, trivy, kube-hunter, kube-bench, docker-bench-security
- **CTF & Forensics**: volatility3, autopsy, sleuthkit, stegsolve, zsteg, photorec
- **OSINT & Intelligence**: sherlock, social-analyzer, recon-ng, maltego, spiderfoot, shodan-cli

## Project Conventions

### Code Style
- **Python Style**: Follow PEP 8 with 4-space indentation
- **File Organization**: Two-script architecture (hexstrike_server.py + hexstrike_mcp.py)
- **Naming Conventions**:
  - Classes: PascalCase (e.g., `IntelligentDecisionEngine`, `ModernVisualEngine`)
  - Functions/Methods: snake_case (e.g., `execute_command`, `analyze_target`)
  - Constants: UPPER_SNAKE_CASE (e.g., `API_PORT`, `CACHE_SIZE`)
  - Private methods: Leading underscore (e.g., `_format_output`)
- **Color Scheme**: Consistent reddish hacker theme using HexStrikeColors palette
- **Docstrings**: Multi-line docstrings for all classes and complex functions
- **Type Hints**: Use typing annotations for function parameters and returns
- **Error Handling**: Try-except blocks with detailed logging and graceful degradation

### Architecture Patterns

**Two-Script System:**
1. **hexstrike_server.py** - Core Flask API server with intelligent decision engine, AI agents, and tool execution
2. **hexstrike_mcp.py** - MCP client interface for AI agent communication

**Key Components:**
- **IntelligentDecisionEngine** - AI-driven tool selection and parameter optimization
- **AI Agents (12+)**: BugBountyWorkflowManager, CTFWorkflowManager, CVEIntelligenceManager, AIExploitGenerator, VulnerabilityCorrelator, TechnologyDetector, RateLimitDetector
- **ModernVisualEngine** - Real-time dashboards and visual feedback
- **Advanced Caching System** - LRU cache with TTL for command results
- **Process Management** - ThreadPoolExecutor for concurrent tool execution
- **Error Recovery** - FailureRecoverySystem with automatic retry and fallback

**Design Principles:**
- Autonomous operation with minimal human intervention
- Intelligent decision-making over brute-force scanning
- Graceful degradation when tools are unavailable
- Real-time feedback with visual progress indicators
- Security-first approach with proper authorization checks

### Testing Strategy
- **Manual Testing**: Verify tool integrations against real targets (authorized only)
- **Unit Testing**: Test individual AI agent decision logic
- **Integration Testing**: Validate MCP communication with AI clients (Claude Desktop, VS Code Copilot, Cursor)
- **Security Testing**: Ensure proper authorization checks and safe command execution
- **Performance Testing**: Validate caching, concurrent execution, and resource usage

**Test Environments:**
- Kali Linux 2024.1+ (primary development environment)
- Ubuntu/Debian with security tools installed
- Isolated VM/container environments for penetration testing

### Git Workflow
- **Main Branch**: `master` - Stable release versions
- **Development**: Direct commits to master for rapid iteration
- **Version Tags**: Semantic versioning (v6.0.0, v7.0.0)
- **Commit Style**: Descriptive messages focusing on feature additions and bug fixes
- **Documentation**: README.md maintained alongside code changes

## Domain Context

### Cybersecurity & Penetration Testing
- **Reconnaissance**: Subdomain enumeration, port scanning, service detection, technology fingerprinting
- **Web Application Security**: Directory brute-forcing, SQL injection, XSS, parameter discovery, API security
- **Network Security**: SMB enumeration, RPC scanning, credential harvesting, lateral movement
- **Binary Analysis**: Reverse engineering, exploit development, memory forensics, CTF challenges
- **Cloud Security**: AWS/Azure/GCP auditing, container scanning, Kubernetes security assessment
- **OSINT**: Email harvesting, social media analysis, breach data correlation

### MCP Protocol Integration
- **FastMCP Framework**: Server exposes tools as MCP endpoints
- **AI Client Support**: Claude Desktop, VS Code Copilot, Cursor, Roo Code, 5ire
- **Tool Invocation**: AI agents call MCP tools with natural language parameters
- **Real-time Communication**: Streaming responses for long-running security scans
- **Error Handling**: Graceful failures with detailed error messages to AI agents

### Ethical Use & Legal Compliance
- **Authorized Testing Only**: All tools require proper written authorization
- **Bug Bounty Programs**: Operate within program scope and rules
- **CTF Competitions**: Educational and competitive environments
- **Red Team Exercises**: Organizational approval required
- **Security Research**: Own systems or explicit permission only

## Important Constraints

### Technical Constraints
- **External Tool Dependencies**: Requires 150+ security tools installed separately
- **System Requirements**: Linux/macOS recommended (Windows compatibility limited)
- **Resource Usage**: High CPU/memory consumption during concurrent scans
- **Network Access**: Requires unrestricted internet access for many tools
- **Permissions**: Many tools require root/sudo privileges for full functionality
- **Python Version**: Python 3.8+ required for async/await and type hints

### Ethical & Legal Constraints
- **Authorization Required**: Never test unauthorized targets
- **No Malicious Use**: Platform is defensive security only
- **Data Privacy**: Respect data protection laws and regulations
- **Responsible Disclosure**: Follow coordinated vulnerability disclosure practices
- **Tool Misuse Prevention**: AI agents must verify authorization before testing

### Operational Constraints
- **AI Agent Supervision**: Monitor AI activities through real-time dashboard
- **Rate Limiting**: Respect target rate limits to avoid denial of service
- **Error Recovery**: Handle tool crashes and network failures gracefully
- **Logging & Audit**: Maintain comprehensive logs for security and compliance
- **Isolation**: Run in dedicated VMs or containers for security testing

## External Dependencies

### Required External Systems
- **Chrome/Chromium** - Browser automation via Selenium WebDriver
- **ChromeDriver** - WebDriver for Chrome browser control
- **Security Tools** - 150+ external tools installed from official sources

### Optional External Services
- **Shodan API** - Internet device search and reconnaissance
- **Censys API** - Certificate and host discovery
- **VirusTotal API** - Malware analysis and threat intelligence
- **Have I Been Pwned API** - Breach data correlation
- **GitHub API** - Git repository secret scanning
- **CVE Databases** - National Vulnerability Database (NVD) for CVE intelligence

### MCP Client Integration
- **Claude Desktop** - Configuration via `~/.config/Claude/claude_desktop_config.json`
- **VS Code Copilot** - Configuration via `.vscode/settings.json`
- **Cursor** - Similar to Claude Desktop configuration
- **Roo Code** - MCP-compatible agent integration

### Infrastructure
- **API Server**: Flask server on localhost:8888 (default)
- **MCP Communication**: stdio/HTTP protocol for AI agent communication
- **Process Management**: ThreadPoolExecutor for concurrent tool execution
- **Caching Layer**: In-memory LRU cache with TTL (60-300 seconds)
- **Logging**: Console + file logging (hexstrike.log)
