#!/usr/bin/env python3
"""
Preview RunIT Package - HTML File Browser Preview
Allows users to preview HTML files in their default browser.
"""

import os
import webbrowser
from pathlib import Path
import tempfile
import shutil


class HTMLPreviewer:
    """HTML file previewer."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "RunIT_Preview"
        self.temp_dir.mkdir(exist_ok=True)
    
    def preview_file(self, filepath: str):
        """Preview an HTML file in the browser."""
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                print(f"❌ File not found: {filepath}")
                return False
            
            if file_path.suffix.lower() not in ['.html', '.htm']:
                print(f"❌ Not an HTML file: {filepath}")
                return False
            
            # Copy file to temp directory to avoid file locking issues
            temp_file = self.temp_dir / file_path.name
            shutil.copy2(file_path, temp_file)
            
            # Open in browser
            file_url = f"file://{temp_file.absolute()}"
            webbrowser.open(file_url)
            
            print(f"🌐 Opening {file_path.name} in your default browser...")
            return True
            
        except Exception as e:
            print(f"❌ Preview failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass


def main(args):
    """Main entry point for preview package."""
    if not args:
        print("❌ Please specify an HTML file to preview")
        print("Usage: preview <filename.html>")
        return
    
    previewer = HTMLPreviewer()
    previewer.preview_file(args[0])
