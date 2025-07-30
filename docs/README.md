# 🚀 RunIT - Smart Terminal Assistant for Windows

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/runit/releases)
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

### 🎯 Supported File Types

| Category | Extensions | Execution Method |
|----------|------------|------------------|
| **Programming** | `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.php` | Auto-detected interpreters/compilers |
| **Web** | `.html`, `.css`, `.json`, `.xml` | Default system programs |
| **Scripts** | `.bat`, `.cmd`, `.sh`, `.ps1` | Native execution |
| **Documents** | `.txt`, `.md`, `.log` | Default text editors |

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (Windows-only tool)
- **Python 3.6+** (included with Windows or from [python.org](https://python.org))
- **Optional**: Install interpreters for languages you want to run:
  - [Node.js](https://nodejs.org/) for JavaScript/TypeScript
  - [PHP](https://www.php.net/) for PHP scripts
  - [GCC/MinGW](https://www.mingw-w64.org/) for C/C++ compilation
  - [Java JDK](https://openjdk.java.net/) for Java development

### Installation

1. **Download RunIT**
   ```cmd
   git clone https://github.com/your-repo/runit.git
   cd runit
   
