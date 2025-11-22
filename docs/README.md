# 🚀 RunIT - Smart Terminal Assistant for Windows

[![Version](https://img.shields.io/badge/version-1.3.2-blue.svg)](https://github.com/mrDevRussia/RunIT-CLI-Tool_WINDOWS/releases/new)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/mrDevRussia/RunIT-CLI-Tool_WINDOWS)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

Other platforms:
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/mrDevRussia/RunIT-CLI-Tool_LINUX)

RunIT is a professional open-source Windows-only CLI tool that transforms your command prompt into a smart terminal assistant. It provides seamless execution, creation, and analysis of code files across multiple programming languages, all from within your familiar Windows CMD environment.

## ✨ Features

### 🔧 Core Functionality 

- **🚀 Universal File Execution**: Run scripts in Python, JavaScript, HTML, CSS, PHP, Batch, Shell, C/C++, Java, TypeScript, and more with automatic interpreter detection
- **📝 Smart File Creation**: Generate new files with language-specific boilerplate code and professional templates  
- **🔍 Advanced Search**: Find keywords in files with context, line numbers, and highlighting
- **🛡️ Local Virus Scanning**: Detect suspicious code patterns, obfuscation, and potential malware using pattern-based analysis
- **📊 Comprehensive File Analysis**: Get detailed statistics, code structure analysis, and metadata for any file
- **💡 Interactive Help System**: Context-aware help with examples and detailed command documentation
- **⚡ REPL Interface**: Stay productive with a persistent, interactive command environment
- **🔄 Auto-Update System**: Keep your tool up to date with the latest features and improvements
- **🌐 Static Website Hosting**: Host and preview your static websites or frontend projects locally with a single command, with optional public URL sharing via LocalTunnel

### ⚠️ Important Note on Folder Access

For security reasons, RunIT can only access and manage files within its installation directory. To work with files:
1. Copy or move them into the RunIT tool's directory
2. Create new files directly using RunIT's commands
3. Use the designated folders within the tool's directory structure

## 🛠️ Available Commands

### 🔧 File Execution
```bash
run <filename>                 # Run files with auto-detection

# Examples:
run script.py                 # Execute Python script
run app.js                    # Execute JavaScript with Node.js
run page.html                 # Open HTML in default browser
run program.bat               # Execute batch file
run code.c                    # Compile and run C program
```

### 📝 File Creation
```bash
create <language> <filename>   # Create new files with boilerplate

# Examples:
create python hello.py        # Create Python script
create javascript app.js      # Create JavaScript file
create html index.html        # Create HTML page
create batch script.bat       # Create batch file
```

### 🔍 File Search
```bash
search <keyword> <filename>    # Search for keywords in files

# Examples:
search "function" script.py   # Find all functions
search "TODO" *.txt           # Find TODO comments
search "error" log.txt        # Find error messages
```

### 🛡️ File Scanning
```bash
scan <filename>               # Scan files for suspicious patterns

# Examples:
scan script.py                # Check for malicious code
scan download.exe             # Virus pattern detection
scan suspicious.js            # Analyze JavaScript safety
```

### 📊 File Information
```bash
info <filename>               # Get detailed file information

# Examples:
info document.txt             # Show file stats
info source.py                # Analyze code structure
info data.json                # Content analysis
```

### 📦 Installation System (New in v1.1)
```bash
install <package@latest>      # Install packages
update <package@latest>       # Update packages or tool
version                       # Show version and package status

# Examples:
install preview_RunIT@latest  # Install HTML preview package
install Edit_RunIT@latest     # Install advanced editor package
update RunIT@latest           # Update the main tool
```

### 📁 File Management (New in v1.1)
```bash
show <file_or_directory>      # Show file/directory structure
edit <filename> [editor]      # Edit files with available editors
```

### 🌐 Website Hosting & Deployment (New in v1.2)
```bash
deploy <site_folder>          # Host and preview static websites locally
share                         # Generate public URL for deployed site

# Examples:
deploy website/              # Start local server for website folder
deploy frontend/dist         # Host built frontend project
share                        # Get public URL (requires internet) (This feautre not available right now)
```

The website hosting feature provides:
- 🚀 Instant local server setup for static websites
- 💻 Works fully offline for local development
- 🌍 Optional public URL generation via LocalTunnel
- 📱 Mobile-friendly testing with local network access
- 🔄 Real-time updates as you modify your files

### 📁 Directory Navigation
```bash
go <directory_path>          # Navigate to directory

# Examples:
go C:\Users\Projects        # Change to projects directory
go ..                       # Go up one directory
```
show project/                 # Display directory tree
show main.py                  # Show file details and structure
edit config.txt              # Edit file with default editor
go C:\Users\Projects          # Change to directory
```

### 🎯 Package Commands
```bash
preview <filename.html>       # Preview HTML files in browser (requires preview_RunIT package)
```

### 🔄 Code Conversion (New in v1.2)
```bash
convert <source_file> <target_language>  # Convert code between languages

# Examples:
convert script.js python    # Convert JavaScript to Python
convert code.py javascript  # Convert Python to JavaScript
convert page.html markdown  # Convert HTML to Markdown
```

### 🔧 Utility Commands
```bash
help [command]               # Show help (general or specific)
test                         # Test RunIT functionality
runai                        # Use offline AI assistant
clear                        # Clear the terminal screen
exit / quit                  # Exit RunIT
```

## 🌟 Key Advantages

- **🎯 Simplified Workflow**: Execute and manage multiple file types from a single interface
- **⚡ Rapid Development**: Quick file creation with smart templates and boilerplate code
- **🔍 Enhanced Security**: Built-in virus scanning for safer code execution
- **📊 Deep Insights**: Comprehensive file analysis and statistics
- **🎨 User-Friendly**: Intuitive commands and helpful documentation
- **🔄 Always Updated**: Stay current with automatic updates
- **💻 Windows Optimized**: Designed specifically for Windows environments

RunIT – Tool Patch Update Summary V1.3.2
________________________________________


New command: p2pmsg
Version 1.0.0 - November 18 2025



Overview
- New command: p2pmsg — encrypted peer‑to‑peer messaging with host/guest handshake.
- Version updates: CLI banner and helper now show v1.3.2; package manager and version.txt updated.
- Docs: added a beginner‑friendly P2PMSG guide at docs/P2PMSG_GUIDE.md and linked it from the help menu and docs README.

p2pmsg Highlights
- Encryption: AES‑256‑CBC with per‑message random IV; symmetric key derived from a 16‑digit session code via SHA‑256.
- Privacy: messages are never stored; only minimal session metadata is cached in data/p2p_sessions.json.
- Handshake: simple UDP handshake (HANDSHAKE/HANDSHAKE_ACK) establishes the tunnel; periodic NAT hole‑punch keepalives (PUNCH) help maintain connectivity.
- Modes: Host generates a session code and listens; Guest enters the code, IP, and port to connect.
- Local testing: Guest now accepts "localhost", "local", or blank IP to default to 127.0.0.1, making same‑device tests straightforward.
- Cross‑network: Works on LAN using Host’s IPv4 (e.g., 192.168.x.x); supports internet connections with router UDP port forwarding.

Advantages
- End‑to‑end encryption: secure messaging using a session code‑derived key.
- Lightweight & fast: UDP transport keeps overhead low for near‑real‑time chat.
- Simple UX: interactive prompts guide Host/Guest setup with clear status messages.
- Privacy by design: no message persistence; ephemeral session cache cleared on exit.
- Flexible networking: local loopback (127.0.0.1), LAN IPs, and internet via port forwarding.
- Beginner‑friendly docs: step‑by‑step guide with troubleshooting for firewall/NAT.

How to Use (Quick)
- Host: run p2pmsg, choose Host, share session code and printed port.
- Guest (same device): enter session code, IP as localhost or blank, and the Host port.
- Guest (same LAN): enter session code, Host’s LAN IPv4, and the Host port.
- Guest (internet): enter session code, Host’s public IP, and the forwarded UDP port.

Troubleshooting (Summary)
- Same device: use 127.0.0.1 and exact Host port.
- Same LAN: use Host’s LAN IPv4; allow inbound UDP on Windows Firewall.
- Internet: configure router UDP port forwarding to Host PC; add Windows Firewall inbound rule; use Host’s public IP.
- CGNAT/strict NAT: some ISPs block inbound; consider requesting public IPv4, using IPv6 if supported, or using a VPN/overlay that provides public ports.
- Stable forwarding: if desired, set a fixed UDP port in commands/p2pmsg.py (bind to a chosen port) and forward it.

Related Changes in 1.3.2
- main.py: registered p2pmsg command, updated banner/version display to v1.3.2.
- commands/helper.py: added p2pmsg entry and version bump; help points to docs/P2PMSG_GUIDE.md.
- commands/package_manager.py: updated current version to 1.3.2 for consistency.
- version.txt: created/updated to 1.3.2.
- data/p2p_sessions.json: added for minimal session metadata (cleared on exit).

For detailed instructions and beginner‑friendly steps, see docs/P2PMSG_GUIDE.md.





RunIT – Tool Patch Update Summary V1.3.1
________________________________________


Patch update Version 1.3.1
# Aegis Vanguard (AV) - Security Scanner Package
Version 1.0.0 - August 23 2025

## Package Information
- Name: aegis_vanguard_RunIT
- Description: Security scanner for websites to detect vulnerabilities and provide fix suggestions
- Author: RunIT Team
- License: MIT
- Minimum RunIT Version: 1.3.0

## Features
- Comprehensive scanning of HTML, JS, PHP, and configuration files
- Risk assessment with severity levels (Critical, High, Medium, Low)
- Detailed reporting in multiple formats (JSON, HTML, PDF)
- Fix suggestions for each detected vulnerability

## Commands
- av <website_folder>: Scan website folder for security vulnerabilities

## Vulnerability Detection Capabilities

### Enhanced SQL Injection Detection
- Improved pattern matching to reduce false positives
- Detects SQL injection in JavaScript query construction
- Severity: High
- Fix: Use Prepared Statements or ORM instead of raw queries

### Cross-Site Request Forgery (CSRF) Detection
- Identifies forms without CSRF protection tokens
- Detects JavaScript form submissions without proper validation
- Severity: High
- Fix: Implement anti-CSRF tokens in all forms and validate them on form submission

### Insecure Direct Object Reference (IDOR) Detection
- Identifies direct references to user IDs, account IDs, and other sensitive identifiers
- Detects unvalidated parameter usage in requests
- Severity: High
- Fix: Implement proper access control checks and use indirect references

### Insecure Deserialization Detection
- Identifies unsafe deserialization of user-controlled data
- Detects parsing of untrusted JSON and other serialized formats
- Severity: Critical
- Fix: Validate and sanitize data before deserialization, use safer alternatives like JSON

### Additional Detections
- Debug Mode: Identifies development/debug settings in production code
- Weak Authentication: Detects weak password storage and authentication mechanisms

## Dependencies
- colorama: For colored terminal output
- reportlab: For PDF report generation
- jinja2: For HTML report generation

## Example Usage



Patch update Version 1.3.2
# p2pmsg Update - Private messaging terminal
Version 1.0.0 - November 18 2025



Overview
- New command: p2pmsg — encrypted peer‑to‑peer messaging with host/guest handshake.
- Version updates: CLI banner and helper now show v1.3.2; package manager and version.txt updated.
- Docs: added a beginner‑friendly P2PMSG guide at docs/P2PMSG_GUIDE.md and linked it from the help menu and docs README.

p2pmsg Highlights
- Encryption: AES‑256‑CBC with per‑message random IV; symmetric key derived from a 16‑digit session code via SHA‑256.
- Privacy: messages are never stored; only minimal session metadata is cached in data/p2p_sessions.json.
- Handshake: simple UDP handshake (HANDSHAKE/HANDSHAKE_ACK) establishes the tunnel; periodic NAT hole‑punch keepalives (PUNCH) help maintain connectivity.
- Modes: Host generates a session code and listens; Guest enters the code, IP, and port to connect.
- Local testing: Guest now accepts "localhost", "local", or blank IP to default to 127.0.0.1, making same‑device tests straightforward.
- Cross‑network: Works on LAN using Host’s IPv4 (e.g., 192.168.x.x); supports internet connections with router UDP port forwarding.

Advantages
- End‑to‑end encryption: secure messaging using a session code‑derived key.
- Lightweight & fast: UDP transport keeps overhead low for near‑real‑time chat.
- Simple UX: interactive prompts guide Host/Guest setup with clear status messages.
- Privacy by design: no message persistence; ephemeral session cache cleared on exit.
- Flexible networking: local loopback (127.0.0.1), LAN IPs, and internet via port forwarding.
- Beginner‑friendly docs: step‑by‑step guide with troubleshooting for firewall/NAT.

How to Use (Quick)
- Host: run p2pmsg, choose Host, share session code and printed port.
- Guest (same device): enter session code, IP as localhost or blank, and the Host port.
- Guest (same LAN): enter session code, Host’s LAN IPv4, and the Host port.
- Guest (internet): enter session code, Host’s public IP, and the forwarded UDP port.

Troubleshooting (Summary)
- Same device: use 127.0.0.1 and exact Host port.
- Same LAN: use Host’s LAN IPv4; allow inbound UDP on Windows Firewall.
- Internet: configure router UDP port forwarding to Host PC; add Windows Firewall inbound rule; use Host’s public IP.
- CGNAT/strict NAT: some ISPs block inbound; consider requesting public IPv4, using IPv6 if supported, or using a VPN/overlay that provides public ports.
- Stable forwarding: if desired, set a fixed UDP port in commands/p2pmsg.py (bind to a chosen port) and forward it.

Related Changes in 1.3.2
- main.py: registered p2pmsg command, updated banner/version display to v1.3.2.
- commands/helper.py: added p2pmsg entry and version bump; help points to docs/P2PMSG_GUIDE.md.
- commands/package_manager.py: updated current version to 1.3.2 for consistency.
- version.txt: created/updated to 1.3.2.
- data/p2p_sessions.json: added for minimal session metadata (cleared on exit).

For detailed instructions and beginner‑friendly steps, see docs/P2PMSG_GUIDE.md.



Patch update Version 1.3.1
# Aegis Vanguard (AV) - Security Scanner Package
Version 1.0.0 - August 23 2025

## Package Information
- Name: aegis_vanguard_RunIT
- Description: Security scanner for websites to detect vulnerabilities and provide fix suggestions
- Author: RunIT Team
- License: MIT
- Minimum RunIT Version: 1.3.1

## Features
- Comprehensive scanning of HTML, JS, PHP, and configuration files
- Risk assessment with severity levels (Critical, High, Medium, Low)
- Detailed reporting in multiple formats (JSON, HTML, PDF)
- Fix suggestions for each detected vulnerability

## Commands
- av <website_folder>: Scan website folder for security vulnerabilities

## Vulnerability Detection Capabilities

### Enhanced SQL Injection Detection
- Improved pattern matching to reduce false positives
- Detects SQL injection in JavaScript query construction
- Severity: High
- Fix: Use Prepared Statements or ORM instead of raw queries

### Cross-Site Request Forgery (CSRF) Detection
- Identifies forms without CSRF protection tokens
- Detects JavaScript form submissions without proper validation
- Severity: High
- Fix: Implement anti-CSRF tokens in all forms and validate them on form submission

### Insecure Direct Object Reference (IDOR) Detection
- Identifies direct references to user IDs, account IDs, and other sensitive identifiers
- Detects unvalidated parameter usage in requests
- Severity: High
- Fix: Implement proper access control checks and use indirect references

### Insecure Deserialization Detection
- Identifies unsafe deserialization of user-controlled data
- Detects parsing of untrusted JSON and other serialized formats
- Severity: Critical
- Fix: Validate and sanitize data before deserialization, use safer alternatives like JSON

### Additional Detections
- Debug Mode: Identifies development/debug settings in production code
- Weak Authentication: Detects weak password storage and authentication mechanisms

## Dependencies
- colorama: For colored terminal output
- reportlab: For PDF report generation
- jinja2: For HTML report generation





Version 1.3 Major update summary
What's New in Version 1.3.0 (August 5, 2025):

-New Commands:

restart Restart the RunIT tool quickly without closing and reopening Provides a seamless way to refresh the application after updates Maintains your current working directory

uninstall Completely uninstall the RunIT tool from your system Creates a cleanup script that removes all files and settings Provides confirmation prompt to prevent accidental uninstallation

adm Advanced Developer Mode - Access a specialized CLI interface in Powershell window Analyze or manage any file within the tool's project folder Requires the IDER package Provides professional development environment with syntax highlighting

kill / kill RunIT Kill all processes for a specific file or stop all processes of the tool Helps manage resource usage and terminate stuck processes Requires the kill package

-New Packages:

IDER Integrated Development Environment for RunIT Required to use the adm command Features a cool interface that looks like an independent software CLI terminal shape with text highlights Supports advanced input features with auto-completion Includes colorized output for better readability Requires optional dependencies: colorama, prompt_toolkit

kill Kill processes for a specific file or all RunIT processes Usage: kill or kill RunIT Helps manage system resources by terminating unnecessary processes Requires optional dependency: psutil

-Improvements:

Dependency Management Enhanced dependency installation system Added Python version compatibility check (requires Python 3.8+) Improved error handling for missing dependencies Added verification for core Python dependencies Better feedback during installation process

Package System Improved package installation from GitHub Enhanced package registry management Better error handling for package operations Updated package template documentation

Self-Test Functionality Comprehensive system testing for core modules Verification of utility modules Directory structure validation Sample files integrity check Python execution verification

-Bug Fixes:

Fixed issues with package installation system from GitHub Improved error handling in deployment and hosting features Enhanced stability when running multiple commands Fixed process management to prevent orphaned processes





## 📚 Documentation

For detailed documentation on all features and commands, type:
```cmd
help
```

Or for specific command help:
```cmd
help <command>
```

## 🤝 Contributing

We welcome contributions! Feel free to submit issues, feature requests, or pull requests to help improve RunIT.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

💡 **Pro Tips**: 
- Pin RunIT to your taskbar or create a desktop shortcut for quick access!
- Use the `runai` command for AI-powered coding assistance
- Install the preview_RunIT package for enhanced HTML development
