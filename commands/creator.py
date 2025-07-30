"""
File Creator Module for RunIT CLI Tool.
Handles creation of new files with language-specific boilerplate code.
"""

import os
from pathlib import Path
from datetime import datetime
from utils.file_utils import FileUtils
from utils.lang_utils import LanguageUtils
from utils.logger import Logger


class FileCreator:
    """
    Handles creation of new script files with appropriate boilerplate code
    based on the specified programming language.
    """

    def __init__(self):
        """Initialize the FileCreator with utilities."""
        self.file_utils = FileUtils()
        self.lang_utils = LanguageUtils()
        self.logger = Logger()

    def get_boilerplate_code(self, language, filename):
        """
        Generate boilerplate code for the specified language.
        
        Args:
            language (str): Programming language name
            filename (str): Name of the file being created
            
        Returns:
            str: Boilerplate code content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_stem = Path(filename).stem
        
        boilerplates = {
            'python': f'''#!/usr/bin/env python3
"""
{filename} - Python Script
Created: {timestamp}
Author: RunIT User
"""


def main():
    """Main function - entry point of the program."""
    print("Hello, World! This is {filename}")
    
    # Your code here
    pass


if __name__ == "__main__":
    main()
''',

            'javascript': f'''/**
 * {filename} - JavaScript Script
 * Created: {timestamp}
 * Author: RunIT User
 */

// Main function
function main() {{
    console.log("Hello, World! This is {filename}");
    
    // Your code here
}}

// Run the main function
main();
''',

            'html': f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_stem}</title>
    <!-- Created: {timestamp} -->
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f4f4f4;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to {file_stem}</h1>
        <p>This HTML file was created by RunIT on {timestamp}</p>
        
        <!-- Your content here -->
    </div>
    
    <script>
        // Your JavaScript code here
        console.log("Hello from {filename}!");
    </script>
</body>
</html>
''',

            'css': f'''/*
 * {filename} - CSS Stylesheet
 * Created: {timestamp}
 * Author: RunIT User
 */

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}}

/* Container styles */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

/* Header styles */
h1, h2, h3 {{
    margin-bottom: 1rem;
    color: #2c3e50;
}}

/* Your custom styles here */
''',

            'php': f'''<?php
/**
 * {filename} - PHP Script
 * Created: {timestamp}
 * Author: RunIT User
 */

// Main function
function main() {{
    echo "Hello, World! This is {filename}\\n";
    
    // Your code here
}}

// Run the main function
main();

?>
''',

            'batch': f'''@echo off
REM {filename} - Batch Script
REM Created: {timestamp}
REM Author: RunIT User

echo Hello, World! This is {filename}

REM Your batch commands here
pause
''',

            'bash': f'''#!/bin/bash
# {filename} - Bash Script
# Created: {timestamp}
# Author: RunIT User

echo "Hello, World! This is {filename}"

# Your bash commands here
''',

            'c': f'''/*
 * {filename} - C Program
 * Created: {timestamp}
 * Author: RunIT User
 */

#include <stdio.h>
#include <stdlib.h>

int main() {{
    printf("Hello, World! This is {filename}\\n");
    
    // Your code here
    
    return 0;
}}
''',

            'cpp': f'''/*
 * {filename} - C++ Program
 * Created: {timestamp}
 * Author: RunIT User
 */

#include <iostream>
#include <string>

using namespace std;

int main() {{
    cout << "Hello, World! This is {filename}" << endl;
    
    // Your code here
    
    return 0;
}}
''',

            'java': f'''/*
 * {file_stem}.java - Java Program
 * Created: {timestamp}
 * Author: RunIT User
 */

public class {file_stem} {{
    
    public static void main(String[] args) {{
        System.out.println("Hello, World! This is {filename}");
        
        // Your code here
    }}
}}
''',

            'typescript': f'''/*
 * {filename} - TypeScript Script
 * Created: {timestamp}
 * Author: RunIT User
 */

// Main function with proper typing
function main(): void {{
    console.log("Hello, World! This is {filename}");
    
    // Your code here
}}

// Run the main function
main();
''',

            'json': f'''{{
  "name": "{file_stem}",
  "version": "1.0.0",
  "description": "JSON file created by RunIT",
  "created": "{timestamp}",
  "author": "RunIT User",
  "data": {{
    "message": "Hello, World! This is {filename}",
    "items": []
  }}
}}
''',

            'xml': f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- {filename} - XML Document -->
<!-- Created: {timestamp} -->
<!-- Author: RunIT User -->

<root>
    <metadata>
        <name>{file_stem}</name>
        <created>{timestamp}</created>
        <author>RunIT User</author>
    </metadata>
    
    <content>
        <message>Hello, World! This is {filename}</message>
        <!-- Your XML content here -->
    </content>
</root>
''',

            'text': f'''{filename} - Text File
Created: {timestamp}
Author: RunIT User

Hello, World! This is {filename}

Your content goes here...
'''
        }
        
        return boilerplates.get(language, f'# {filename}\n# Created: {timestamp}\n\n# Your code here\n')

    def get_file_extension(self, language):
        """
        Get the appropriate file extension for a language.
        
        Args:
            language (str): Programming language name
            
        Returns:
            str: File extension including the dot
        """
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'js': '.js',
            'html': '.html',
            'css': '.css',
            'php': '.php',
            'batch': '.bat',
            'bat': '.bat',
            'bash': '.sh',
            'shell': '.sh',
            'c': '.c',
            'cpp': '.cpp',
            'c++': '.cpp',
            'java': '.java',
            'typescript': '.ts',
            'ts': '.ts',
            'json': '.json',
            'xml': '.xml',
            'text': '.txt',
            'txt': '.txt'
        }
        
        return extensions.get(language.lower(), '.txt')

    def validate_filename(self, filename):
        """
        Validate filename for Windows compatibility.
        
        Args:
            filename (str): Filename to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Windows invalid characters
        invalid_chars = '<>:"/\\|?*'
        
        # Check for invalid characters
        for char in invalid_chars:
            if char in filename:
                return False, f"Filename contains invalid character: '{char}'"
        
        # Check for reserved names
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        filename_upper = Path(filename).stem.upper()
        if filename_upper in reserved_names:
            return False, f"'{filename}' is a reserved filename in Windows"
        
        # Check length (Windows path limit)
        if len(filename) > 255:
            return False, "Filename is too long (max 255 characters)"
        
        # Check for ending with space or period
        if filename.endswith(' ') or filename.endswith('.'):
            return False, "Filename cannot end with space or period"
        
        return True, ""

    def create_file(self, language, filename):
        """
        Create a new file with boilerplate code for the specified language.
        
        Args:
            language (str): Programming language name
            filename (str): Name of the file to create
        """
        try:
            # Validate filename
            is_valid, error_msg = self.validate_filename(filename)
            if not is_valid:
                print(f"❌ Invalid filename: {error_msg}")
                return
            
            # Auto-add extension if not provided
            file_path = Path(filename)
            if not file_path.suffix:
                extension = self.get_file_extension(language)
                filename = filename + extension
                file_path = Path(filename)
            
            # Check if file already exists
            if file_path.exists():
                response = input(f"⚠️  File '{filename}' already exists. Overwrite? (y/n): ").lower()
                if response not in ['y', 'yes']:
                    print("❌ File creation cancelled")
                    return
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate boilerplate code
            boilerplate = self.get_boilerplate_code(language, filename)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(boilerplate)
            
            # Log and notify
            file_size = self.file_utils.get_file_size(file_path)
            self.logger.info(f"Created file: {file_path} ({file_size})")
            
            print(f"✅ Successfully created '{filename}' with {language} boilerplate")
            print(f"📁 Location: {file_path.resolve()}")
            print(f"📊 Size: {file_size}")
            
            # Show preview of first few lines
            lines = boilerplate.split('\n')
            preview_lines = min(5, len(lines))
            print(f"\n📝 Preview (first {preview_lines} lines):")
            print("-" * 40)
            for i, line in enumerate(lines[:preview_lines], 1):
                print(f"{i:2d}: {line}")
            if len(lines) > preview_lines:
                print(f"    ... ({len(lines) - preview_lines} more lines)")
            print("-" * 40)
            
        except PermissionError:
            print(f"❌ Permission denied: Cannot create file '{filename}'")
        except OSError as e:
            print(f"❌ OS Error: {e}")
        except Exception as e:
            self.logger.error(f"Error creating file {filename}: {e}")
            print(f"❌ Error creating file: {e}")

    def list_supported_languages(self):
        """
        Return a list of supported programming languages.
        
        Returns:
            list: List of supported language names
        """
        return [
            'python', 'javascript', 'html', 'css', 'php', 'batch', 'bash',
            'c', 'cpp', 'java', 'typescript', 'json', 'xml', 'text'
        ]
