#!/usr/bin/env python3
"""
Example RunIT Package Template
Demonstrates the basic structure of a RunIT package.

Author: Your Name
Version: 1.0.0
License: MIT
"""

from typing import List, Optional
from pathlib import Path

class ExamplePackage:
    """Example package implementation for RunIT CLI Tool."""

    def __init__(self):
        """Initialize the package."""
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
        if command == "example":
            return self._example_command(args)
        return False

    def _example_command(self, args: List[str]) -> bool:
        """Example command implementation.

        Args:
            args: Command arguments

        Returns:
            bool: True if command executed successfully
        """
        try:
            if not args:
                print("❌ Please provide an argument")
                print("Usage: example <argument>")
                return False

            # Implement your command logic here
            argument = args[0]
            print(f"✅ Example command executed with argument: {argument}")
            return True

        except Exception as e:
            print(f"❌ Error executing example command: {str(e)}")
            return False

# Create package instance
package = ExamplePackage()

# This function will be called by RunIT to handle commands
def handle_command(command: str, args: List[str]) -> bool:
    """Entry point for package commands."""
    return package.handle_command(command, args)