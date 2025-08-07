# IDER for RunIT CLI Tool

## Overview
IDER (Integrated Development Environment for RunIT) is a specialized development environment that enhances the RunIT CLI Tool with advanced features and a professional interface. It provides a dedicated CLI environment that looks and feels like an independent software application.

## Features
- Professional CLI interface with syntax highlighting
- Advanced file management capabilities
- Project analysis tools
- Integrated file editing
- Process management for RunIT applications
- Customizable interface with themes

## Installation
```bash
runit install IDER_RunIT@latest
```

## Usage
To enter the Advanced Developer Mode:
```bash
python main.py adm [directory]
```
or simply:
```bash
runit adm [directory]
```

If no directory is specified, the current directory will be used.

### Commands within ADM Mode
- `edit <file>` - Open file in the integrated editor
- `analyze <file/dir>` - Analyze code structure and quality
- `list [dir]` - List files with enhanced display
- `search <pattern> [dir]` - Advanced search with syntax highlighting
- `run <file>` - Execute file with output capture
- `kill <process>` - Terminate a running process
- `theme <name>` - Change the interface theme
- `exit` - Exit ADM mode and return to RunIT

## Benefits
1. **Professional Environment**: Dedicated interface for serious development work
2. **Enhanced Productivity**: Specialized tools for faster development
3. **Integrated Workflow**: Seamless transition between coding, testing, and execution
4. **Process Management**: Better control over running applications

## Requirements
- RunIT CLI Tool v1.3.0 or higher
- Python 3.8+
- Dependencies: colorama, prompt_toolkit

## License
MIT License

## Author
RunIT Team