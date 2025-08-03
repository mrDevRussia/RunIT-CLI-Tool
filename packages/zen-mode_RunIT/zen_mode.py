#!/usr/bin/env python3
"""
Zen Mode Package for RunIT CLI Tool
Provides a minimal, focused coding interface.

Version: 1.0.0
License: MIT
"""

import os
import time
import random
from typing import List, Optional

# Global instance
_zen_mode_instance = None

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function required by RunIT."""
    global _zen_mode_instance
    if _zen_mode_instance is None:
        _zen_mode_instance = ZenMode()
    return _zen_mode_instance.handle_command(command, args)

class ZenMode:
    """Zen Mode implementation for focused coding."""

    def __init__(self):
        """Initialize Zen Mode."""
        self.name = "zen-mode_RunIT"
        self.version = "1.0.0"
        self.phrases = [
            "Focus on the present line",
            "Code flows like water",
            "One line, one thought",
            "Clarity comes from simplicity",
            "Breathe and code",
            "In the zone",
            "Mind like water",
            "Present moment awareness"
        ]

    def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle zen mode commands.

        Args:
            command: The command to execute
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if command == "zen":
            return self._zen_mode(args)
        return False

    def _zen_mode(self, args: List[str]) -> bool:
        """Enter zen mode for focused coding.

        Args:
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if not args:
            print("Error: Please provide a file path")
            return False

        file_path = args[0]
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n" * 2)
                print(f"Line {i}/{len(lines)}:")
                print("\n" * 2)
                print(line.rstrip())
                print("\n" * 2)
                print(random.choice(self.phrases))
                print("\n" * 2)
                print("Press Enter to continue, Ctrl+C to exit")
                input()

            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

# Create a global instance of ZenMode
_zen_mode_instance = ZenMode()

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function for package integration.

    Args:
        command: The command to execute
        args: List of command arguments

    Returns:
        bool: True if command was handled successfully
    """
    return _zen_mode_instance.handle_command(command, args)