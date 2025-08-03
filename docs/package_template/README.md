# Creating RunIT Packages

## Overview
This guide explains how to create and publish packages for the RunIT CLI Tool. Each package should be hosted in its own GitHub repository and follow the structure outlined below.

## Package Structure
```
package_name/
├── package_info.json   # Package metadata and configuratio
├── your_package_name.py  # Main package implementation (Change the file name to the name of package)
├── README.md           # Package documentation
└── requirements.txt    # Python dependencies (if any)
```

## Package Configuration
Every package must include a `package_info.json` file with the following structure:

```json
{
    "name": "your_package_name",
    "version": "1.0.0",
    "description": "Package description",
    "author": "Your Name",
    "main_file": "main.py",
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

## Publishing Your Package
1. Create a new GitHub repository named `your-package-runit`
2. Structure your package following the template above
3. Submit a pull request to the RunIT package registry to add your package

## Installation
Users can install your package using:
```bash
runit install your_package_name
```

## Best Practices
1. Follow Python coding standards (PEP 8)
2. Include comprehensive documentation
3. Add error handling and logging
4. Test your package thoroughly
5. Keep dependencies minimal
6. Use semantic versioning

## Example Package
Check out our example packages:
- [preview-runit](https://github.com/runit-packages/preview-runit)
- [edit-runit](https://github.com/runit-packages/edit-runit)