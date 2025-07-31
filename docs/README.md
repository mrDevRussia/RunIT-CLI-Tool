# 🚀 RunIT - Smart Terminal Assistant for Windows

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/runit/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

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
go <directory_path>          # Navigate to directory

# Examples:
show project/                 # Display directory tree
show main.py                  # Show file details and structure
edit config.txt              # Edit file with default editor
go C:\Users\Projects          # Change to directory
```

### 🎯 Package Commands
```bash
preview <filename.html>       # Preview HTML files in browser (requires preview_RunIT package)
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

