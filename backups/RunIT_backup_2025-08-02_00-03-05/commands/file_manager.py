#!/usr/bin/env python3
"""
File Manager for RunIT CLI Tool
Handles file operations like show, edit, and directory navigation.

Author: RunIT Development Team
Version: 1.1.0
License: MIT
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from utils.logger import Logger
from utils.file_utils import FileUtils


class FileManager:
    """
    Manages file operations for the RunIT CLI tool.
    Handles file structure display, editing, and directory navigation.
    """

    def __init__(self):
        """Initialize the File Manager."""
        self.logger = Logger()
        self.file_utils = FileUtils()
        
        # Current working directory tracking
        self.current_dir = Path.cwd()

    def show_file_structure(self, filepath: str, max_depth: int = 3) -> bool:
        """
        Show the file structure of a file or directory.
        
        Args:
            filepath (str): Path to file or directory
            max_depth (int): Maximum depth to traverse for directories
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = Path(filepath).resolve()
            
            if not target_path.exists():
                print(f"❌ Path not found: {filepath}")
                return False
            
            print(f"\n📁 File Structure: {target_path.name}")
            print("="*50)
            
            if target_path.is_file():
                self._show_file_info(target_path)
            else:
                self._show_directory_tree(target_path, max_depth)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to show file structure: {e}")
            self.logger.error(f"Show file structure failed: {e}")
            return False

    def _show_file_info(self, file_path: Path):
        """Show detailed information about a single file."""
        try:
            stat = file_path.stat()
            
            print(f"📄 File: {file_path.name}")
            print(f"   Size: {self._format_size(stat.st_size)}")
            print(f"   Type: {file_path.suffix or 'No extension'}")
            print(f"   Modified: {self._format_time(stat.st_mtime)}")
            
            # Show file content structure for code files
            if self._is_code_file(file_path):
                self._show_code_structure(file_path)
                
        except Exception as e:
            print(f"❌ Failed to show file info: {e}")

    def _show_directory_tree(self, dir_path: Path, max_depth: int, current_depth: int = 0):
        """Show directory tree structure."""
        if current_depth >= max_depth:
            return
        
        indent = "    " * current_depth
        
        try:
            items = []
            for item in dir_path.iterdir():
                if not item.name.startswith('.'):  # Skip hidden files
                    items.append(item)
            
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                prefix = "└── " if is_last else "├── "
                
                if item.is_directory():
                    print(f"{indent}{prefix}📁 {item.name}/")
                    if current_depth < max_depth - 1:
                        self._show_directory_tree(item, max_depth, current_depth + 1)
                else:
                    icon = self._get_file_icon(item)
                    size = self._format_size(item.stat().st_size)
                    print(f"{indent}{prefix}{icon} {item.name} ({size})")
                    
        except PermissionError:
            print(f"{indent}❌ Permission denied")
        except Exception as e:
            print(f"{indent}❌ Error: {e}")

    def _show_code_structure(self, file_path: Path):
        """Show structure of code files (functions, classes, etc.)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            structure = []
            for i, line in enumerate(lines[:100], 1):  # Limit to first 100 lines
                stripped = line.strip()
                
                # Python
                if file_path.suffix == '.py':
                    if stripped.startswith('def ') or stripped.startswith('class '):
                        structure.append(f"   Line {i:3}: {stripped}")
                
                # JavaScript/TypeScript
                elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    if 'function ' in stripped or stripped.startswith('class '):
                        structure.append(f"   Line {i:3}: {stripped}")
                
                # Java/C#
                elif file_path.suffix in ['.java', '.cs']:
                    if 'public class ' in stripped or 'private class ' in stripped:
                        structure.append(f"   Line {i:3}: {stripped}")
            
            if structure:
                print("\n🔍 Code Structure:")
                for item in structure[:10]:  # Show max 10 items
                    print(item)
                if len(structure) > 10:
                    print(f"   ... and {len(structure) - 10} more items")
                    
        except Exception as e:
            self.logger.error(f"Failed to analyze code structure: {e}")

    def edit_file(self, filepath: str, editor: Optional[str] = None) -> bool:
        """
        Edit a file using specified or default editor.
        
        Args:
            filepath (str): Path to file to edit
            editor (str): Optional editor preference
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(filepath)
            
            # Create file if it doesn't exist
            if not file_path.exists():
                print(f"📝 Creating new file: {filepath}")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()
            
            # Check if Edit_RunIT package is installed
            if self._is_edit_package_available():
                return self._use_edit_package(filepath, editor)
            else:
                return self._use_builtin_editor(file_path)
                
        except Exception as e:
            print(f"❌ Edit failed: {e}")
            self.logger.error(f"File edit failed: {e}")
            return False

    def _is_edit_package_available(self) -> bool:
        """Check if Edit_RunIT package is installed."""
        try:
            packages_dir = Path("packages")
            edit_package = packages_dir / "Edit_RunIT"
            return edit_package.exists() and (edit_package / "editor.py").exists()
        except:
            return False

    def _use_edit_package(self, filepath: str, editor_name: Optional[str] = None) -> bool:
        """Use the Edit_RunIT package for editing."""
        try:
            # Import and use the edit package
            packages_path = str(Path("packages/Edit_RunIT"))
            if packages_path not in sys.path:
                sys.path.insert(0, packages_path)
            
            # Import the editor module
            import importlib.util
            spec = importlib.util.spec_from_file_location("editor", Path("packages/Edit_RunIT/editor.py"))
            if spec and spec.loader:
                editor_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(editor_module)
                
                args = [filepath]
                if editor_name:
                    args.append(editor_name)
                
                editor_module.main(args)
                return True
            else:
                raise ImportError("Could not load editor module")
            
        except Exception as e:
            print(f"❌ Edit package failed: {e}")
            return self._use_builtin_editor(Path(filepath))

    def _use_builtin_editor(self, file_path: Path) -> bool:
        """Use built-in editor (notepad on Windows)."""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['notepad.exe', str(file_path)])
            else:
                # Try common editors on other systems
                editors = ['nano', 'vim', 'gedit']
                for editor in editors:
                    try:
                        subprocess.run([editor, str(file_path)])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    print("❌ No suitable editor found")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Editor launch failed: {e}")
            return False

    def go_to_directory(self, directory_path: str) -> bool:
        """
        Navigate to a directory.
        
        Args:
            directory_path (str): Path to directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = Path(directory_path).resolve()
            
            if not target_path.exists():
                print(f"❌ Directory not found: {directory_path}")
                return False
            
            if not target_path.is_dir():
                print(f"❌ Not a directory: {directory_path}")
                return False
            
            # Change to the directory
            os.chdir(target_path)
            self.current_dir = target_path
            
            print(f"📁 Changed to directory: {target_path}")
            
            # Show directory contents
            print("\n📋 Directory contents:")
            self._show_directory_contents(target_path)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to change directory: {e}")
            self.logger.error(f"Directory change failed: {e}")
            return False

    def _show_directory_contents(self, dir_path: Path):
        """Show contents of a directory."""
        try:
            items = []
            for item in dir_path.iterdir():
                if not item.name.startswith('.'):  # Skip hidden files
                    items.append(item)
            
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            if dirs:
                print("   Directories:")
                for directory in dirs[:10]:  # Show max 10
                    print(f"     📁 {directory.name}/")
                if len(dirs) > 10:
                    print(f"     ... and {len(dirs) - 10} more directories")
            
            if files:
                print("   Files:")
                for file in files[:10]:  # Show max 10
                    icon = self._get_file_icon(file)
                    size = self._format_size(file.stat().st_size)
                    print(f"     {icon} {file.name} ({size})")
                if len(files) > 10:
                    print(f"     ... and {len(files) - 10} more files")
                    
        except Exception as e:
            print(f"❌ Failed to show directory contents: {e}")

    def get_current_directory(self) -> str:
        """Get the current working directory."""
        return str(self.current_dir)

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file."""
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cs', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs'}
        return file_path.suffix.lower() in code_extensions

    def _get_file_icon(self, file_path: Path) -> str:
        """Get appropriate icon for file type."""
        suffix = file_path.suffix.lower()
        
        icons = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.html': '🌐', '.css': '🎨',
            '.java': '☕', '.cpp': '⚙️', '.c': '⚙️', '.cs': '🔷', '.php': '🐘',
            '.rb': '💎', '.go': '🐹', '.rs': '🦀', '.json': '📋', '.xml': '📋',
            '.md': '📝', '.txt': '📄', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.mp3': '🎵', '.mp4': '🎥', '.avi': '🎥', '.zip': '📦', '.tar': '📦'
        }
        
        return icons.get(suffix, '📄')

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _format_time(self, timestamp: float) -> str:
        """Format timestamp in human readable format."""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")