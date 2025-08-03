#!/usr/bin/env python3
"""
ilovebeans Package for RunIT CLI Tool
Provides a minimal, focused coding interface.
Version: 1.0.0
License: MIT
"""

import os
import time
import random
from typing import List, Optional

# Global instance
_ilovebeans_instance = None

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function required by RunIT."""
    global _ilovebeans_instance
    if _ilovebeans_instance is None:
       _ilovebeans_instance = ilovebeans()
    return _ilovebeans_instance.handle_command(command, args)

class ilovebeans:
    """Bean implementation for fun coding."""

    def __init__(self):
        """Initialize ilovebeans."""
        self.name = "ilovebeans_RunIT"
        self.version = "1.0.0"
        self.phrases = [
            "I love beans!"
                 ]

    def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle ilovebeans commands.

        Args:
            command: The command to execute
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if command == "bean":
            return self._ilovebeans(args)
        return False

    def _ilovebeans(self, args: List[str]) -> bool:
        """ilovebeans for fun coding.

        Args:
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if not args:
            print("I love beans!")
            return False

# Create a global instance of ilovebeans
_ilovebeans_instance = ilovebeans()

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function for package integration.

    Args:
        command: The command to execute
        args: List of command arguments

    Returns:
        bool: True if command was handled successfully
    """
    return _ilovebeans_instance.handle_command(command, args)