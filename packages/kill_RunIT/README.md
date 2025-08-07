# Kill Package for RunIT

## Overview
The Kill package provides functionality to terminate processes for specific files or all RunIT processes. This is useful for cleaning up resources and stopping runaway processes during development.

## Features
- Terminate processes associated with a specific file
- Kill all RunIT-related processes with a single command
- Cross-platform support (Windows, macOS, Linux)
- Enhanced process detection with psutil (when available)

## Installation
This package is included with RunIT v1.3.0 and above. No additional installation is required.

If you're using an older version of RunIT, you can install it manually:

```
run install kill
```

## Dependencies
The Kill package works best with the `psutil` Python package, which provides enhanced process detection capabilities. While not strictly required, it's highly recommended:

```
pip install psutil
```

## Usage

### Kill processes for a specific file
```
kill <file_path>
```
This will terminate all processes that are running or using the specified file.

### Kill all RunIT processes
```
kill RunIT
```
This will terminate all RunIT-related processes (except the current process).

## Examples

```
# Kill processes for a specific Python script
kill C:\path\to\script.py

# Kill processes for a Node.js application
kill C:\path\to\app.js

# Kill all RunIT processes
kill RunIT
```

## How It Works
The Kill package uses different methods to detect and terminate processes:

1. With psutil (recommended):
   - Scans all running processes
   - Checks command lines and open files
   - Precisely identifies processes related to the target

2. Without psutil (fallback):
   - Uses platform-specific commands (tasklist/taskkill on Windows, ps/kill on Unix)
   - Basic matching based on process names and command lines
   - Limited to certain file types (.py, .js, .bat)

## License
MIT

## Author
RunIT Team