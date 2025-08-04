# RunIT Package Development Guide

## Overview
This guide explains how to create and publish packages for the RunIT CLI Tool. Each package must be hosted in its own GitHub repository and follow the structure outlined below.

## Package Structure Requirements
Your package repository must contain these files:

```
package_name/
├── package_info.json   # Required: Package metadata and configuration
├── your_package_name.py  # Required: Main package implementation
├── README.md           # Required: Package documentation
└── requirements.txt    # Optional: Python dependencies
```

## Package Configuration
The `package_info.json` file is mandatory and must include:

```json
{
    "name": "your_package_name",
    "version": "1.0.0",
    "description": "Package description",
    "author": "Your Name",
    "main_file": "your_package_name.py",
    "dependencies": [],
    "commands": {
        "command_name": {
            "description": "Command description",
            "usage": "command_name <arguments>"
        }
    },
    "minimum_runit_version": "1.2.0",
    "license": "MIT"
}
```

## Package Implementation
Your main Python file must:
1. Define a main class for your package
2. Implement the `handle_command` method
3. Follow this structure:

```python
class YourPackageName:
    def __init__(self):
        self.name = "your_package_name"
        self.version = "1.0.0"

    def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle package commands.
        Args:
            command: The command to execute
            args: List of command arguments
        Returns:
            bool: True if command was handled successfully
        """
        if command == "your_command":
            return self._your_command(args)
        return False
```

## Publishing Steps
1. Create a GitHub repository named `your-package-name_RunIT`
2. Implement your package following the structure above
3. Add your package to RunIT's package sources by updating `package_sources.json`:

```json
{
  "sources": [
    {
      "name": "your-package-name_RunIT",
      "repository": "https://github.com/username/your-package-name_RunIT",
      "install_command": "runit install your-package-name_RunIT@latest",
      "description": "Your package description",
      "author": "Your Name",
      "tags": ["your-tags"],
      "verified": false,
      "last_updated": "YYYY-MM-DD"
    }
  ]
}
```

Note: The package sources file is backed up automatically. You can find the backup at `package_sources_backup.json`.

## Installation
Users will install your package using:
```bash
install your_package_name_RunIT@latest
```

## Best Practices
1. Follow Python coding standards (PEP 8)
2. Include comprehensive documentation
3. Test your package thoroughly
4. Keep dependencies minimal
5. Handle errors gracefully
6. Provide clear usage examples
7. Use semantic versioning

## Support
For questions or issues, please:
1. Check the RunIT documentation
2. Open an issue in your package repository
3. Contact the RunIT maintainers