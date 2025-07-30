"""
File Utilities Module for RunIT CLI Tool.
Provides common file operations and utilities.
"""

import os
import shutil
from pathlib import Path


class FileUtils:
    """
    Utility class for file operations and file system helpers.
    Provides methods for file size calculations, path handling, and other common operations.
    """

    @staticmethod
    def get_file_size(file_path):
        """
        Get human-readable file size.
        
        Args:
            file_path (Path or str): Path to the file
            
        Returns:
            str: Formatted file size (e.g., "1.5 KB", "2.3 MB")
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            size_bytes = file_path.stat().st_size
            
            # Define size units
            units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
            unit_index = 0
            size = float(size_bytes)
            
            # Convert to appropriate unit
            while size >= 1024.0 and unit_index < len(units) - 1:
                size /= 1024.0
                unit_index += 1
            
            # Format based on size
            if unit_index == 0:  # Bytes
                return f"{int(size)} {units[unit_index]}"
            else:
                return f"{size:.1f} {units[unit_index]}"
                
        except (OSError, AttributeError):
            return "Unknown size"

    @staticmethod
    def is_text_file(file_path, sample_size=8192):
        """
        Check if a file is likely a text file by examining its content.
        
        Args:
            file_path (Path or str): Path to the file
            sample_size (int): Number of bytes to sample for analysis
            
        Returns:
            bool: True if file appears to be text, False otherwise
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
            
            if not sample:
                return True  # Empty file is considered text
            
            # Check for null bytes (common in binary files)
            if b'\x00' in sample:
                return False
            
            # Check for high percentage of printable characters
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                try:
                    sample.decode('latin-1')
                    # Additional checks for latin-1 decoded content
                    printable_chars = sum(1 for byte in sample if 32 <= byte <= 126 or byte in [9, 10, 13])
                    ratio = printable_chars / len(sample)
                    return ratio > 0.7
                except UnicodeDecodeError:
                    return False
                    
        except (OSError, IOError):
            return False

    @staticmethod
    def get_file_extension_info(extension):
        """
        Get information about a file extension.
        
        Args:
            extension (str): File extension (with or without dot)
            
        Returns:
            dict: Information about the file extension
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        extension = extension.lower()
        
        extension_info = {
            # Programming languages
            '.py': {'type': 'Python Script', 'category': 'Programming', 'interpreter': 'python'},
            '.js': {'type': 'JavaScript', 'category': 'Programming', 'interpreter': 'node'},
            '.ts': {'type': 'TypeScript', 'category': 'Programming', 'interpreter': 'ts-node'},
            '.java': {'type': 'Java Source', 'category': 'Programming', 'interpreter': 'javac+java'},
            '.c': {'type': 'C Source', 'category': 'Programming', 'interpreter': 'gcc'},
            '.cpp': {'type': 'C++ Source', 'category': 'Programming', 'interpreter': 'g++'},
            '.php': {'type': 'PHP Script', 'category': 'Programming', 'interpreter': 'php'},
            '.rb': {'type': 'Ruby Script', 'category': 'Programming', 'interpreter': 'ruby'},
            '.pl': {'type': 'Perl Script', 'category': 'Programming', 'interpreter': 'perl'},
            '.go': {'type': 'Go Source', 'category': 'Programming', 'interpreter': 'go'},
            '.rs': {'type': 'Rust Source', 'category': 'Programming', 'interpreter': 'rustc'},
            
            # Web technologies
            '.html': {'type': 'HTML Document', 'category': 'Web', 'interpreter': 'browser'},
            '.htm': {'type': 'HTML Document', 'category': 'Web', 'interpreter': 'browser'},
            '.css': {'type': 'CSS Stylesheet', 'category': 'Web', 'interpreter': 'browser'},
            '.scss': {'type': 'SASS Stylesheet', 'category': 'Web', 'interpreter': 'sass'},
            '.less': {'type': 'LESS Stylesheet', 'category': 'Web', 'interpreter': 'lessc'},
            
            # Scripts
            '.bat': {'type': 'Batch Script', 'category': 'Script', 'interpreter': 'cmd'},
            '.cmd': {'type': 'Command Script', 'category': 'Script', 'interpreter': 'cmd'},
            '.sh': {'type': 'Shell Script', 'category': 'Script', 'interpreter': 'bash'},
            '.ps1': {'type': 'PowerShell Script', 'category': 'Script', 'interpreter': 'powershell'},
            
            # Data formats
            '.json': {'type': 'JSON Data', 'category': 'Data', 'interpreter': 'text_editor'},
            '.xml': {'type': 'XML Data', 'category': 'Data', 'interpreter': 'text_editor'},
            '.yaml': {'type': 'YAML Data', 'category': 'Data', 'interpreter': 'text_editor'},
            '.yml': {'type': 'YAML Data', 'category': 'Data', 'interpreter': 'text_editor'},
            '.csv': {'type': 'CSV Data', 'category': 'Data', 'interpreter': 'spreadsheet'},
            '.txt': {'type': 'Text File', 'category': 'Document', 'interpreter': 'text_editor'},
            '.md': {'type': 'Markdown', 'category': 'Document', 'interpreter': 'text_editor'},
            '.log': {'type': 'Log File', 'category': 'Document', 'interpreter': 'text_editor'},
            
            # Configuration
            '.ini': {'type': 'Configuration', 'category': 'Config', 'interpreter': 'text_editor'},
            '.cfg': {'type': 'Configuration', 'category': 'Config', 'interpreter': 'text_editor'},
            '.conf': {'type': 'Configuration', 'category': 'Config', 'interpreter': 'text_editor'},
            
            # Archives
            '.zip': {'type': 'ZIP Archive', 'category': 'Archive', 'interpreter': 'archive_tool'},
            '.rar': {'type': 'RAR Archive', 'category': 'Archive', 'interpreter': 'archive_tool'},
            '.7z': {'type': '7-Zip Archive', 'category': 'Archive', 'interpreter': 'archive_tool'},
            '.tar': {'type': 'TAR Archive', 'category': 'Archive', 'interpreter': 'archive_tool'},
            
            # Executables
            '.exe': {'type': 'Executable', 'category': 'Executable', 'interpreter': 'direct'},
            '.msi': {'type': 'Installer', 'category': 'Executable', 'interpreter': 'direct'},
            '.dll': {'type': 'Library', 'category': 'Executable', 'interpreter': 'system'},
        }
        
        return extension_info.get(extension, {
            'type': 'Unknown',
            'category': 'Unknown',
            'interpreter': 'unknown'
        })

    @staticmethod
    def safe_filename(filename):
        """
        Create a safe filename by removing/replacing invalid characters.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Safe filename for Windows
        """
        # Windows invalid characters
        invalid_chars = '<>:"/\\|?*'
        
        # Replace invalid characters with underscore
        safe_name = filename
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')
        
        # Handle reserved names
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = Path(safe_name).stem.upper()
        if name_without_ext in reserved_names:
            safe_name = '_' + safe_name
        
        # Limit length (Windows has 255 character limit for filenames)
        if len(safe_name) > 255:
            name_part = Path(safe_name).stem[:240]  # Leave room for extension
            ext_part = Path(safe_name).suffix
            safe_name = name_part + ext_part
        
        return safe_name

    @staticmethod
    def create_backup(file_path, backup_suffix='.bak'):
        """
        Create a backup copy of a file.
        
        Args:
            file_path (Path or str): Path to the file to backup
            backup_suffix (str): Suffix for backup file
            
        Returns:
            Path: Path to backup file, or None if failed
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            if not file_path.exists():
                return None
            
            backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
            
            # If backup already exists, add number
            counter = 1
            while backup_path.exists():
                backup_path = file_path.with_suffix(f'{file_path.suffix}{backup_suffix}.{counter}')
                counter += 1
            
            shutil.copy2(file_path, backup_path)
            return backup_path
            
        except (OSError, IOError):
            return None

    @staticmethod
    def get_directory_size(directory_path):
        """
        Calculate total size of a directory and its contents.
        
        Args:
            directory_path (Path or str): Path to directory
            
        Returns:
            tuple: (total_size_bytes, formatted_size_string)
        """
        try:
            if isinstance(directory_path, str):
                directory_path = Path(directory_path)
            
            total_size = 0
            
            for item in directory_path.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, IOError):
                        continue  # Skip files we can't access
            
            # Format size
            formatted_size = FileUtils.get_file_size_from_bytes(total_size)
            return total_size, formatted_size
            
        except (OSError, IOError):
            return 0, "Unknown"

    @staticmethod
    def get_file_size_from_bytes(size_bytes):
        """
        Convert bytes to human-readable format.
        
        Args:
            size_bytes (int): Size in bytes
            
        Returns:
            str: Formatted size string
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"

    @staticmethod
    def find_files(directory, pattern='*', recursive=True):
        """
        Find files matching a pattern in a directory.
        
        Args:
            directory (Path or str): Directory to search
            pattern (str): File pattern to match
            recursive (bool): Whether to search subdirectories
            
        Returns:
            list: List of matching file paths
        """
        try:
            if isinstance(directory, str):
                directory = Path(directory)
            
            if not directory.exists() or not directory.is_dir():
                return []
            
            if recursive:
                return list(directory.rglob(pattern))
            else:
                return list(directory.glob(pattern))
                
        except (OSError, IOError):
            return []

    @staticmethod
    def get_file_permissions(file_path):
        """
        Get file permissions in a readable format.
        
        Args:
            file_path (Path or str): Path to the file
            
        Returns:
            dict: Permission information
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            return {
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK),
                'exists': file_path.exists(),
                'is_file': file_path.is_file(),
                'is_directory': file_path.is_dir(),
                'is_symlink': file_path.is_symlink()
            }
        except (OSError, IOError):
            return {
                'readable': False,
                'writable': False,
                'executable': False,
                'exists': False,
                'is_file': False,
                'is_directory': False,
                'is_symlink': False
            }
