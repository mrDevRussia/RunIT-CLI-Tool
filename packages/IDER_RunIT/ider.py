#!/usr/bin/env python3
"""
IDER (Integrated Development Environment for RunIT)
Provides a professional CLI interface for development within RunIT.

Version: 1.0.0
License: MIT
"""

import os
import sys
import shutil
import subprocess
import time
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

# Try to import optional dependencies
try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    print("Warning: colorama not installed. Colors will be disabled.")
    print("Install with: pip install colorama")
    # Create dummy color classes
    class DummyColors:
        def __getattr__(self, name):
            return ''
    Fore = Back = Style = DummyColors()

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import PathCompleter, WordCompleter
    from prompt_toolkit.styles import Style as PromptStyle
    from prompt_toolkit.history import FileHistory
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False
    print("Warning: prompt_toolkit not installed. Advanced input features will be disabled.")
    print("Install with: pip install prompt_toolkit")

# Global instance
_ider_instance = None

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function required by RunIT."""
    global _ider_instance
    if _ider_instance is None:
        _ider_instance = IDER()
    return _ider_instance.handle_command(command, args)

class IDER:
    """Integrated Development Environment for RunIT."""

    def __init__(self):
        """Initialize the IDER environment."""
        self.name = "IDER_RunIT"
        self.version = "1.0.0"
        self.current_dir = os.getcwd()
        self.running_processes: Dict[int, subprocess.Popen] = {}
        self.process_counter = 0
        self.history_file = os.path.join(os.path.expanduser("~"), ".runit_ider_history")
        self.theme = "default"
        self.themes = {
            "default": {
                "prompt": Fore.CYAN + Style.BRIGHT,
                "path": Fore.GREEN,
                "command": Fore.WHITE + Style.BRIGHT,
                "error": Fore.RED + Style.BRIGHT,
                "success": Fore.GREEN + Style.BRIGHT,
                "info": Fore.BLUE + Style.BRIGHT,
                "highlight": Fore.YELLOW,
                "reset": Style.RESET_ALL
            },
            "dark": {
                "prompt": Fore.BLUE + Style.BRIGHT,
                "path": Fore.MAGENTA,
                "command": Fore.WHITE + Style.BRIGHT,
                "error": Fore.RED + Style.BRIGHT,
                "success": Fore.GREEN + Style.BRIGHT,
                "info": Fore.CYAN + Style.BRIGHT,
                "highlight": Fore.YELLOW,
                "reset": Style.RESET_ALL
            },
            "light": {
                "prompt": Fore.BLUE,
                "path": Fore.GREEN,
                "command": Fore.BLACK + Style.BRIGHT,
                "error": Fore.RED,
                "success": Fore.GREEN,
                "info": Fore.BLUE,
                "highlight": Fore.MAGENTA,
                "reset": Style.RESET_ALL
            }
        }
        
        # Initialize commands
        self.commands = {
            "help": self._cmd_help,
            "edit": self._cmd_edit,
            "analyze": self._cmd_analyze,
            "list": self._cmd_list,
            "search": self._cmd_search,
            "run": self._cmd_run,
            "kill": self._cmd_kill,
            "theme": self._cmd_theme,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
            "clear": self._cmd_clear,
            "processes": self._cmd_processes,
            "info": self._cmd_info
        }

    def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle package commands.

        Args:
            command: The command to execute
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if command == "adm":
            # Check if --independent flag is provided
            if "--independent" in args or "-i" in args:
                # Remove the flag from args
                args = [arg for arg in args if arg not in ["--independent", "-i"]]
                return self._launch_independent_adm(args)
            else:
                # Launch ADM using the batch file to open in PowerShell
                script_dir = os.path.dirname(os.path.abspath(__file__))
                batch_file = os.path.join(script_dir, "adm.bat")
                
                # Execute the batch file
                try:
                    subprocess.Popen(batch_file, shell=True)
                    print(f"✅ Advanced Developer Mode launched in a separate window.")
                    return True
                except Exception as e:
                    print(f"Error launching ADM: {str(e)}")
                    return self._adm_mode(args)  # Fallback to inline mode
        return False

    def _launch_independent_adm(self, args: List[str]) -> bool:
        """Launch Advanced Developer Mode in an independent PowerShell window.

        Args:
            args: Command arguments, optional directory path

        Returns:
            bool: True if command executed successfully
        """
        try:
            # Determine the target directory
            target_dir = os.getcwd()
            if args and os.path.isdir(args[0]):
                target_dir = os.path.abspath(args[0])

            # Get the path to the main script
            script_path = os.path.abspath(__file__)
            
            # Create a temporary PowerShell script to launch ADM
            temp_script_path = os.path.join(os.environ.get('TEMP', '.'), 'launch_adm.ps1')
            
            with open(temp_script_path, 'w') as f:
                f.write(f"""# PowerShell script to launch ADM in independent window
# Set window title
$Host.UI.RawUI.WindowTitle = "RunIT - Advanced Developer Mode (PowerShell)"

# Set working directory
Set-Location -Path \"{target_dir}\"

# Add necessary paths
$env:PYTHONPATH = \"{os.path.dirname(os.path.dirname(script_path))};$env:PYTHONPATH\"

# Import the IDER module
$scriptPath = \"{script_path}\"

# Run Python with the ADM mode - using PowerShell syntax
& python -c "import sys; sys.path.insert(0, r'{os.path.dirname(os.path.dirname(script_path))}'); from packages.IDER_RunIT.ider import IDER; ider = IDER(); ider._adm_mode([r'{target_dir}']);"

# Keep window open after completion
Write-Host "\nPress any key to close this window..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
""")
            
            # Launch PowerShell with the script - ensure it opens in PowerShell window
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 1  # SW_SHOWNORMAL
            
            # Use PowerShell.exe with -NoExit to ensure it stays in PowerShell
            subprocess.Popen(
                ['powershell.exe', '-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', 
                 f'& {{Clear-Host; . "{temp_script_path}"}}'],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print(f"✅ Advanced Developer Mode launched in a separate window.")
            return True
            
        except Exception as e:
            print(f"Error launching independent ADM: {str(e)}")
            return False

    def _adm_mode(self, args: List[str]) -> bool:
        """Enter Advanced Developer Mode.

        Args:
            args: Command arguments, optional directory path

        Returns:
            bool: True if command executed successfully
        """
        try:
            # Change to specified directory if provided
            if args and os.path.isdir(args[0]):
                self.current_dir = os.path.abspath(args[0])
                os.chdir(self.current_dir)
            
            # Display welcome banner
            self._display_banner()
            
            # Main REPL loop
            running = True
            while running:
                try:
                    # Get user input with advanced prompt if available
                    if HAS_PROMPT_TOOLKIT:
                        # Create completers
                        path_completer = PathCompleter()
                        command_completer = WordCompleter(list(self.commands.keys()))
                        
                        # Create prompt style
                        style = PromptStyle.from_dict({
                            'prompt': '#00FFFF bold',
                            'path': '#00FF00',
                        })
                        
                        # Create history
                        history = FileHistory(self.history_file)
                        
                        # Display prompt
                        prompt_text = f"{self.themes[self.theme]['prompt']}ADM{Style.RESET_ALL} {self.themes[self.theme]['path']}{os.path.basename(self.current_dir)}{Style.RESET_ALL}> "
                        user_input = prompt(prompt_text, completer=command_completer, style=style, history=history)
                    else:
                        # Fallback to basic input
                        prompt_text = f"{self.themes[self.theme]['prompt']}ADM{Style.RESET_ALL} {self.themes[self.theme]['path']}{os.path.basename(self.current_dir)}{Style.RESET_ALL}> "
                        user_input = input(prompt_text)
                    
                    # Skip empty inputs
                    if not user_input.strip():
                        continue
                    
                    # Parse command and arguments
                    parts = user_input.strip().split()
                    cmd = parts[0].lower()
                    cmd_args = parts[1:] if len(parts) > 1 else []
                    
                    # Execute command
                    if cmd in self.commands:
                        result = self.commands[cmd](cmd_args)
                        if cmd == "exit" and result:
                            running = False
                    else:
                        print(f"{self.themes[self.theme]['error']}Unknown command: {cmd}{Style.RESET_ALL}")
                        print("Type 'help' to see available commands")
                        
                except KeyboardInterrupt:
                    print("\n" + self.themes[self.theme]['info'] + "Use 'exit' to return to RunIT" + Style.RESET_ALL)
                except EOFError:
                    running = False
                except Exception as e:
                    print(f"{self.themes[self.theme]['error']}Error: {str(e)}{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"Error starting Advanced Developer Mode: {str(e)}")
            return False

    def _display_banner(self):
        """Display the IDER welcome banner."""
        terminal_width = shutil.get_terminal_size().columns
        banner_width = min(80, terminal_width)
        
        # Create banner with dynamic width
        banner = f"""
{'═' * banner_width}
{' ' * ((banner_width - 36) // 2)}IDER - Advanced Developer Mode v{self.version}{' ' * ((banner_width - 36) // 2)}
{' ' * ((banner_width - 44) // 2)}Integrated Development Environment for RunIT{' ' * ((banner_width - 44) // 2)}
{'═' * banner_width}
{' ' * ((banner_width - 50) // 2)}Type 'help' for commands | 'exit' to return to RunIT{' ' * ((banner_width - 50) // 2)}
{'═' * banner_width}
"""
        
        # Print with colors
        colored_banner = banner.replace('═', f"{Fore.CYAN}═{Style.RESET_ALL}")
        print(colored_banner)

    def _cmd_help(self, args: List[str]) -> bool:
        """Display help information."""
        if args and args[0] in self.commands:
            # Show specific command help
            cmd = args[0]
            help_text = {
                "help": "Display help information for commands\nUsage: help [command]",
                "edit": "Open file in the integrated editor\nUsage: edit <file>",
                "analyze": "Analyze code structure and quality\nUsage: analyze <file/dir>",
                "list": "List files with enhanced display\nUsage: list [dir]",
                "search": "Advanced search with syntax highlighting\nUsage: search <pattern> [dir]",
                "run": "Execute file with output capture\nUsage: run <file>",
                "kill": "Terminate a running process\nUsage: kill <process_id>",
                "theme": "Change the interface theme\nUsage: theme <name>\nAvailable themes: default, dark, light",
                "cd": "Change current directory\nUsage: cd <directory>",
                "exit": "Exit ADM mode and return to RunIT\nUsage: exit",
                "clear": "Clear the terminal screen\nUsage: clear",
                "processes": "List all running processes\nUsage: processes",
                "info": "Show information about files or directories\nUsage: info <file/dir>"
            }
            
            print(f"\n{self.themes[self.theme]['command']}{cmd.upper()}{Style.RESET_ALL}")
            print(f"{self.themes[self.theme]['info']}{help_text.get(cmd, 'No help available')}{Style.RESET_ALL}")
            
        else:
            # Show general help
            print(f"\n{self.themes[self.theme]['command']}IDER COMMANDS:{Style.RESET_ALL}")
            print(f"{self.themes[self.theme]['info']}")
            print("  help [command]      - Display help information")
            print("  edit <file>         - Open file in the integrated editor")
            print("  analyze <file/dir>  - Analyze code structure and quality")
            print("  list [dir]          - List files with enhanced display")
            print("  search <pattern>    - Advanced search with syntax highlighting")
            print("  run <file>          - Execute file with output capture")
            print("  kill <process_id>   - Terminate a running process")
            print("  theme <name>        - Change the interface theme")
            print("  cd <directory>      - Change current directory")
            print("  processes           - List all running processes")
            print("  info <file/dir>     - Show information about files or directories")
            print("  clear               - Clear the terminal screen")
            print("  exit                - Exit ADM mode and return to RunIT")
            print(f"{Style.RESET_ALL}")
            
        return True

    def _cmd_edit(self, args: List[str]) -> bool:
        """Open file in the integrated editor."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a file to edit{Style.RESET_ALL}")
            print("Usage: edit <file>")
            return False
            
        filepath = args[0]
        if not os.path.exists(filepath):
            print(f"{self.themes[self.theme]['error']}Error: File not found: {filepath}{Style.RESET_ALL}")
            return False
            
        # Try to use system default editor
        try:
            if os.name == 'nt':  # Windows
                os.system(f'notepad "{filepath}"')
            else:  # Unix-like
                if 'EDITOR' in os.environ:
                    os.system(f'{os.environ["EDITOR"]} "{filepath}"')
                else:
                    # Try common editors
                    for editor in ['nano', 'vim', 'vi', 'emacs']:
                        try:
                            subprocess.run(['which', editor], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            os.system(f'{editor} "{filepath}"')
                            break
                        except subprocess.CalledProcessError:
                            continue
                    else:
                        print(f"{self.themes[self.theme]['error']}No suitable editor found. Set the EDITOR environment variable.{Style.RESET_ALL}")
                        return False
            return True
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error opening editor: {str(e)}{Style.RESET_ALL}")
            return False

    def _cmd_analyze(self, args: List[str]) -> bool:
        """Analyze code structure and quality."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a file or directory to analyze{Style.RESET_ALL}")
            print("Usage: analyze <file/dir>")
            return False
            
        path = args[0]
        if not os.path.exists(path):
            print(f"{self.themes[self.theme]['error']}Error: Path not found: {path}{Style.RESET_ALL}")
            return False
            
        print(f"{self.themes[self.theme]['info']}Analyzing {path}...{Style.RESET_ALL}")
        
        if os.path.isfile(path):
            self._analyze_file(path)
        else:
            self._analyze_directory(path)
            
        return True

    def _analyze_file(self, filepath: str) -> None:
        """Analyze a single file."""
        # Get file extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        # Get file size
        size = os.path.getsize(filepath)
        size_str = self._format_size(size)
        
        # Get file stats
        stats = os.stat(filepath)
        modified = time.ctime(stats.st_mtime)
        
        # Print basic info
        print(f"\n{self.themes[self.theme]['command']}File Analysis: {os.path.basename(filepath)}{Style.RESET_ALL}")
        print(f"{self.themes[self.theme]['info']}Path:{Style.RESET_ALL} {filepath}")
        print(f"{self.themes[self.theme]['info']}Size:{Style.RESET_ALL} {size_str}")
        print(f"{self.themes[self.theme]['info']}Modified:{Style.RESET_ALL} {modified}")
        
        # Count lines
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            blank_lines = total_lines - code_lines - comment_lines
            
            print(f"{self.themes[self.theme]['info']}Total Lines:{Style.RESET_ALL} {total_lines}")
            print(f"{self.themes[self.theme]['info']}Code Lines:{Style.RESET_ALL} {code_lines}")
            print(f"{self.themes[self.theme]['info']}Comment Lines:{Style.RESET_ALL} {comment_lines}")
            print(f"{self.themes[self.theme]['info']}Blank Lines:{Style.RESET_ALL} {blank_lines}")
            
            # Language-specific analysis
            if ext == '.py':
                self._analyze_python(lines)
            elif ext in ['.js', '.ts']:
                self._analyze_javascript(lines)
            elif ext == '.html':
                self._analyze_html(lines)
            elif ext == '.css':
                self._analyze_css(lines)
            elif ext in ['.json', '.jsonc']:
                self._analyze_json(filepath)
                
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error analyzing file: {str(e)}{Style.RESET_ALL}")

    def _analyze_directory(self, dirpath: str) -> None:
        """Analyze a directory."""
        print(f"\n{self.themes[self.theme]['command']}Directory Analysis: {os.path.basename(dirpath)}{Style.RESET_ALL}")
        
        # Count files by type
        file_types = {}
        total_size = 0
        total_files = 0
        total_dirs = 0
        
        for root, dirs, files in os.walk(dirpath):
            total_dirs += len(dirs)
            total_files += len(files)
            
            for file in files:
                filepath = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                ext = ext.lower() if ext else 'no_extension'
                
                # Count file type
                file_types[ext] = file_types.get(ext, 0) + 1
                
                # Add to total size
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        
        # Print summary
        print(f"{self.themes[self.theme]['info']}Total Size:{Style.RESET_ALL} {self._format_size(total_size)}")
        print(f"{self.themes[self.theme]['info']}Files:{Style.RESET_ALL} {total_files}")
        print(f"{self.themes[self.theme]['info']}Directories:{Style.RESET_ALL} {total_dirs}")
        
        # Print file types
        print(f"\n{self.themes[self.theme]['command']}File Types:{Style.RESET_ALL}")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            ext_name = ext[1:] if ext.startswith('.') else ext
            print(f"{self.themes[self.theme]['info']}{ext_name}:{Style.RESET_ALL} {count}")

    def _analyze_python(self, lines: List[str]) -> None:
        """Analyze Python code."""
        # Count imports
        imports = [line for line in lines if re.match(r'^\s*import\s+|^\s*from\s+\w+\s+import', line)]
        
        # Count functions and classes
        functions = [line for line in lines if re.match(r'^\s*def\s+\w+\s*\(', line)]
        classes = [line for line in lines if re.match(r'^\s*class\s+\w+', line)]
        
        print(f"\n{self.themes[self.theme]['command']}Python Analysis:{Style.RESET_ALL}")
        print(f"{self.themes[self.theme]['info']}Imports:{Style.RESET_ALL} {len(imports)}")
        print(f"{self.themes[self.theme]['info']}Functions:{Style.RESET_ALL} {len(functions)}")
        print(f"{self.themes[self.theme]['info']}Classes:{Style.RESET_ALL} {len(classes)}")

    def _analyze_javascript(self, lines: List[str]) -> None:
        """Analyze JavaScript/TypeScript code."""
        # Count imports
        imports = [line for line in lines if re.search(r'(import|require)\s*\(|import\s+.+\s+from', line)]
        
        # Count functions
        functions = [line for line in lines if re.search(r'function\s+\w+\s*\(|\w+\s*=\s*function|\w+\s*\(.*\)\s*=>|\w+\s*\(.*\)\s*{', line)]
        
        # Count classes
        classes = [line for line in lines if re.search(r'class\s+\w+', line)]
        
        print(f"\n{self.themes[self.theme]['command']}JavaScript Analysis:{Style.RESET_ALL}")
        print(f"{self.themes[self.theme]['info']}Imports/Requires:{Style.RESET_ALL} {len(imports)}")
        print(f"{self.themes[self.theme]['info']}Functions:{Style.RESET_ALL} {len(functions)}")
        print(f"{self.themes[self.theme]['info']}Classes:{Style.RESET_ALL} {len(classes)}")

    def _analyze_html(self, lines: List[str]) -> None:
        """Analyze HTML code."""
        # Join all lines to handle multi-line tags
        content = ''.join(lines)
        
        # Count tags
        tags = re.findall(r'<\s*([a-zA-Z0-9]+)[^>]*>', content)
        tag_counts = {}
        for tag in tags:
            tag_counts[tag.lower()] = tag_counts.get(tag.lower(), 0) + 1
        
        # Check for common elements
        has_doctype = bool(re.search(r'<!DOCTYPE\s+html>', content, re.IGNORECASE))
        has_head = bool(re.search(r'<head[^>]*>.*?</head>', content, re.DOTALL | re.IGNORECASE))
        has_body = bool(re.search(r'<body[^>]*>.*?</body>', content, re.DOTALL | re.IGNORECASE))
        has_scripts = bool(re.search(r'<script[^>]*>.*?</script>', content, re.DOTALL | re.IGNORECASE))
        has_styles = bool(re.search(r'<style[^>]*>.*?</style>', content, re.DOTALL | re.IGNORECASE))
        has_links = bool(re.search(r'<link[^>]*>', content, re.IGNORECASE))
        
        print(f"\n{self.themes[self.theme]['command']}HTML Analysis:{Style.RESET_ALL}")
        print(f"{self.themes[self.theme]['info']}Total Tags:{Style.RESET_ALL} {len(tags)}")
        print(f"{self.themes[self.theme]['info']}Doctype:{Style.RESET_ALL} {'Yes' if has_doctype else 'No'}")
        print(f"{self.themes[self.theme]['info']}Head Section:{Style.RESET_ALL} {'Yes' if has_head else 'No'}")
        print(f"{self.themes[self.theme]['info']}Body Section:{Style.RESET_ALL} {'Yes' if has_body else 'No'}")
        print(f"{self.themes[self.theme]['info']}Scripts:{Style.RESET_ALL} {'Yes' if has_scripts else 'No'}")
        print(f"{self.themes[self.theme]['info']}Styles:{Style.RESET_ALL} {'Yes' if has_styles else 'No'}")
        print(f"{self.themes[self.theme]['info']}External Links:{Style.RESET_ALL} {'Yes' if has_links else 'No'}")
        
        # Print top 5 tags
        print(f"\n{self.themes[self.theme]['command']}Top 5 Tags:{Style.RESET_ALL}")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{self.themes[self.theme]['info']}{tag}:{Style.RESET_ALL} {count}")

    def _analyze_css(self, lines: List[str]) -> None:
        """Analyze CSS code."""
        # Join all lines to handle multi-line rules
        content = ''.join(lines)
        
        # Count selectors
        selectors = re.findall(r'([^{]+){', content)
        selectors = [s.strip() for s in selectors if s.strip()]
        
        # Count properties
        properties = re.findall(r'([\w-]+)\s*:', content)
        property_counts = {}
        for prop in properties:
            property_counts[prop.lower()] = property_counts.get(prop.lower(), 0) + 1
        
        # Count media queries
        media_queries = re.findall(r'@media\s+[^{]+{', content)
        
        # Count keyframes
        keyframes = re.findall(r'@keyframes\s+[^{]+{', content)
        
        print(f"\n{self.themes[self.theme]['command']}CSS Analysis:{Style.RESET_ALL}")
        print(f"{self.themes[self.theme]['info']}Selectors:{Style.RESET_ALL} {len(selectors)}")
        print(f"{self.themes[self.theme]['info']}Properties:{Style.RESET_ALL} {len(properties)}")
        print(f"{self.themes[self.theme]['info']}Media Queries:{Style.RESET_ALL} {len(media_queries)}")
        print(f"{self.themes[self.theme]['info']}Keyframes:{Style.RESET_ALL} {len(keyframes)}")
        
        # Print top 5 properties
        print(f"\n{self.themes[self.theme]['command']}Top 5 Properties:{Style.RESET_ALL}")
        for prop, count in sorted(property_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{self.themes[self.theme]['info']}{prop}:{Style.RESET_ALL} {count}")

    def _analyze_json(self, filepath: str) -> None:
        """Analyze JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Analyze structure
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"\n{self.themes[self.theme]['command']}JSON Analysis:{Style.RESET_ALL}")
                print(f"{self.themes[self.theme]['info']}Type:{Style.RESET_ALL} Object")
                print(f"{self.themes[self.theme]['info']}Keys:{Style.RESET_ALL} {len(keys)}")
                
                # Print top 5 keys
                if keys:
                    print(f"\n{self.themes[self.theme]['command']}Top Keys:{Style.RESET_ALL}")
                    for key in keys[:5]:
                        value_type = type(data[key]).__name__
                        print(f"{self.themes[self.theme]['info']}{key}:{Style.RESET_ALL} {value_type}")
                        
            elif isinstance(data, list):
                print(f"\n{self.themes[self.theme]['command']}JSON Analysis:{Style.RESET_ALL}")
                print(f"{self.themes[self.theme]['info']}Type:{Style.RESET_ALL} Array")
                print(f"{self.themes[self.theme]['info']}Items:{Style.RESET_ALL} {len(data)}")
                
                # Analyze first item if it's an object
                if data and isinstance(data[0], dict):
                    keys = list(data[0].keys())
                    print(f"{self.themes[self.theme]['info']}First Item Keys:{Style.RESET_ALL} {len(keys)}")
                    
                    # Print top 5 keys of first item
                    if keys:
                        print(f"\n{self.themes[self.theme]['command']}First Item Keys:{Style.RESET_ALL}")
                        for key in keys[:5]:
                            value_type = type(data[0][key]).__name__
                            print(f"{self.themes[self.theme]['info']}{key}:{Style.RESET_ALL} {value_type}")
                            
        except json.JSONDecodeError:
            print(f"{self.themes[self.theme]['error']}Invalid JSON format{Style.RESET_ALL}")
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error analyzing JSON: {str(e)}{Style.RESET_ALL}")

    def _cmd_list(self, args: List[str]) -> bool:
        """List files with enhanced display."""
        # Get directory path
        dirpath = args[0] if args else self.current_dir
        
        if not os.path.isdir(dirpath):
            print(f"{self.themes[self.theme]['error']}Error: Not a directory: {dirpath}{Style.RESET_ALL}")
            return False
            
        try:
            # Get directory contents
            entries = os.listdir(dirpath)
            dirs = []
            files = []
            
            # Separate directories and files
            for entry in entries:
                path = os.path.join(dirpath, entry)
                if os.path.isdir(path):
                    dirs.append((entry, path))
                else:
                    files.append((entry, path))
                    
            # Sort alphabetically
            dirs.sort(key=lambda x: x[0].lower())
            files.sort(key=lambda x: x[0].lower())
            
            # Print directories
            if dirs:
                print(f"\n{self.themes[self.theme]['command']}Directories:{Style.RESET_ALL}")
                for name, path in dirs:
                    print(f"{self.themes[self.theme]['info']}📁 {name}/{Style.RESET_ALL}")
                    
            # Print files by type
            if files:
                print(f"\n{self.themes[self.theme]['command']}Files:{Style.RESET_ALL}")
                for name, path in files:
                    # Get file extension
                    _, ext = os.path.splitext(name)
                    ext = ext.lower()
                    
                    # Choose icon based on extension
                    icon = self._get_file_icon(ext)
                    
                    # Get file size
                    try:
                        size = os.path.getsize(path)
                        size_str = self._format_size(size)
                    except OSError:
                        size_str = "??"
                        
                    # Print file with icon and size
                    print(f"{icon} {name} {self.themes[self.theme]['highlight']}({size_str}){Style.RESET_ALL}")
                    
            # Print summary
            print(f"\n{self.themes[self.theme]['info']}Total: {len(dirs)} directories, {len(files)} files{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error listing directory: {str(e)}{Style.RESET_ALL}")
            return False

    def _cmd_search(self, args: List[str]) -> bool:
        """Advanced search with syntax highlighting."""
        if len(args) < 1:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a search pattern{Style.RESET_ALL}")
            print("Usage: search <pattern> [dir]")
            return False
            
        pattern = args[0]
        dirpath = args[1] if len(args) > 1 else self.current_dir
        
        if not os.path.exists(dirpath):
            print(f"{self.themes[self.theme]['error']}Error: Path not found: {dirpath}{Style.RESET_ALL}")
            return False
            
        try:
            # Compile regex pattern
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                # If not a valid regex, use as literal string
                pattern = re.escape(pattern)
                regex = re.compile(pattern, re.IGNORECASE)
                
            # Track results
            results = []
            
            # Search function for a single file
            def search_file(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append((filepath, i, line.rstrip()))
                except Exception:
                    # Skip files that can't be read
                    pass
            
            # Search in directory or single file
            if os.path.isdir(dirpath):
                print(f"{self.themes[self.theme]['info']}Searching for '{pattern}' in {dirpath}...{Style.RESET_ALL}")
                
                # Walk directory tree
                for root, _, files in os.walk(dirpath):
                    for file in files:
                        # Skip binary files and very large files
                        filepath = os.path.join(root, file)
                        if self._is_text_file(filepath) and os.path.getsize(filepath) < 10_000_000:  # 10MB limit
                            search_file(filepath)
            else:
                # Search in single file
                print(f"{self.themes[self.theme]['info']}Searching for '{pattern}' in {dirpath}...{Style.RESET_ALL}")
                search_file(dirpath)
                
            # Display results
            if results:
                print(f"\n{self.themes[self.theme]['success']}Found {len(results)} matches:{Style.RESET_ALL}\n")
                
                # Group by file
                files = {}
                for filepath, line_num, line in results:
                    if filepath not in files:
                        files[filepath] = []
                    files[filepath].append((line_num, line))
                    
                # Display results by file
                for filepath, matches in files.items():
                    rel_path = os.path.relpath(filepath, self.current_dir)
                    print(f"{self.themes[self.theme]['command']}{rel_path}{Style.RESET_ALL}")
                    
                    for line_num, line in matches:
                        # Highlight matches in the line
                        highlighted = line
                        for match in regex.finditer(line):
                            start, end = match.span()
                            highlighted = highlighted[:start] + self.themes[self.theme]['highlight'] + highlighted[start:end] + Style.RESET_ALL + highlighted[end:]
                            
                        print(f"  {self.themes[self.theme]['info']}{line_num}:{Style.RESET_ALL} {highlighted}")
                    print()
            else:
                print(f"{self.themes[self.theme]['info']}No matches found.{Style.RESET_ALL}")
                
            return True
            
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error during search: {str(e)}{Style.RESET_ALL}")
            return False

    def _cmd_run(self, args: List[str]) -> bool:
        """Execute file with output capture."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a file to run{Style.RESET_ALL}")
            print("Usage: run <file>")
            return False
            
        filepath = args[0]
        if not os.path.exists(filepath):
            print(f"{self.themes[self.theme]['error']}Error: File not found: {filepath}{Style.RESET_ALL}")
            return False
            
        # Get file extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        # Determine command based on file type
        cmd = None
        if ext == '.py':
            cmd = ['python', filepath]
        elif ext == '.js':
            cmd = ['node', filepath]
        elif ext == '.html':
            # Open HTML in default browser
            import webbrowser
            webbrowser.open(filepath)
            print(f"{self.themes[self.theme]['success']}Opened {filepath} in default browser{Style.RESET_ALL}")
            return True
        elif ext == '.bat' or ext == '.cmd':
            cmd = [filepath]
        elif ext == '.sh':
            cmd = ['bash', filepath]
        else:
            print(f"{self.themes[self.theme]['error']}Unsupported file type: {ext}{Style.RESET_ALL}")
            return False
            
        try:
            # Run the command
            print(f"{self.themes[self.theme]['info']}Running {filepath}...{Style.RESET_ALL}\n")
            
            # Create process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Store process
            self.process_counter += 1
            process_id = self.process_counter
            self.running_processes[process_id] = process
            
            print(f"{self.themes[self.theme]['info']}Process ID: {process_id}{Style.RESET_ALL}")
            print(f"{self.themes[self.theme]['info']}Use 'kill {process_id}' to terminate{Style.RESET_ALL}\n")
            
            # Print separator
            print(f"{self.themes[self.theme]['command']}{'=' * 40}{Style.RESET_ALL}")
            
            # Read output in real-time
            for line in process.stdout:
                print(line.rstrip())
                
            # Wait for process to complete
            process.wait()
            
            # Print separator
            print(f"{self.themes[self.theme]['command']}{'=' * 40}{Style.RESET_ALL}")
            
            # Check for errors
            stderr = process.stderr.read()
            if stderr:
                print(f"{self.themes[self.theme]['error']}Errors:{Style.RESET_ALL}")
                print(stderr)
                
            # Print exit code
            exit_code = process.returncode
            if exit_code == 0:
                print(f"{self.themes[self.theme]['success']}Process completed successfully (exit code: {exit_code}){Style.RESET_ALL}")
            else:
                print(f"{self.themes[self.theme]['error']}Process failed with exit code: {exit_code}{Style.RESET_ALL}")
                
            # Remove from running processes
            if process_id in self.running_processes:
                del self.running_processes[process_id]
                
            return True
            
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error running file: {str(e)}{Style.RESET_ALL}")
            return False

    def _cmd_kill(self, args: List[str]) -> bool:
        """Terminate a running process."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a process ID{Style.RESET_ALL}")
            print("Usage: kill <process_id>")
            return False
            
        try:
            # Check if killing all RunIT processes
            if args[0].lower() == "runit":
                print(f"{self.themes[self.theme]['info']}Terminating all RunIT processes...{Style.RESET_ALL}")
                
                # Kill all running processes
                for pid, process in list(self.running_processes.items()):
                    try:
                        process.terminate()
                        print(f"{self.themes[self.theme]['success']}Terminated process {pid}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{self.themes[self.theme]['error']}Failed to terminate process {pid}: {str(e)}{Style.RESET_ALL}")
                        
                # Clear running processes
                self.running_processes.clear()
                return True
                
            # Kill specific process
            process_id = int(args[0])
            if process_id not in self.running_processes:
                print(f"{self.themes[self.theme]['error']}Error: Process {process_id} not found{Style.RESET_ALL}")
                return False
                
            # Terminate process
            process = self.running_processes[process_id]
            process.terminate()
            
            # Remove from running processes
            del self.running_processes[process_id]
            
            print(f"{self.themes[self.theme]['success']}Process {process_id} terminated{Style.RESET_ALL}")
            return True
            
        except ValueError:
            print(f"{self.themes[self.theme]['error']}Error: Invalid process ID{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error terminating process: {str(e)}{Style.RESET_ALL}")
            return False

    def _cmd_theme(self, args: List[str]) -> bool:
        """Change the interface theme."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a theme{Style.RESET_ALL}")
            print("Usage: theme <name>")
            print("Available themes: default, dark, light")
            return False
            
        theme_name = args[0].lower()
        if theme_name not in self.themes:
            print(f"{self.themes[self.theme]['error']}Error: Unknown theme: {theme_name}{Style.RESET_ALL}")
            print("Available themes: default, dark, light")
            return False
            
        self.theme = theme_name
        print(f"{self.themes[self.theme]['success']}Theme changed to {theme_name}{Style.RESET_ALL}")
        return True

    def _cmd_cd(self, args: List[str]) -> bool:
        """Change current directory."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a directory{Style.RESET_ALL}")
            print("Usage: cd <directory>")
            return False
            
        dirpath = args[0]
        
        # Handle special cases
        if dirpath == '..':
            dirpath = os.path.dirname(self.current_dir)
        elif dirpath == '~':
            dirpath = os.path.expanduser('~')
        elif not os.path.isabs(dirpath):
            dirpath = os.path.join(self.current_dir, dirpath)
            
        if not os.path.isdir(dirpath):
            print(f"{self.themes[self.theme]['error']}Error: Not a directory: {dirpath}{Style.RESET_ALL}")
            return False
            
        # Change directory
        os.chdir(dirpath)
        self.current_dir = dirpath
        print(f"{self.themes[self.theme]['success']}Changed to {dirpath}{Style.RESET_ALL}")
        return True

    def _cmd_exit(self, args: List[str]) -> bool:
        """Exit ADM mode and return to RunIT."""
        # Kill all running processes
        for pid, process in list(self.running_processes.items()):
            try:
                process.terminate()
                print(f"{self.themes[self.theme]['info']}Terminated process {pid}{Style.RESET_ALL}")
            except:
                pass
                
        print(f"{self.themes[self.theme]['success']}Exiting Advanced Developer Mode{Style.RESET_ALL}")
        return True

    def _cmd_clear(self, args: List[str]) -> bool:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self._display_banner()
        return True

    def _cmd_processes(self, args: List[str]) -> bool:
        """List all running processes."""
        if not self.running_processes:
            print(f"{self.themes[self.theme]['info']}No running processes{Style.RESET_ALL}")
            return True
            
        print(f"\n{self.themes[self.theme]['command']}Running Processes:{Style.RESET_ALL}")
        for pid, process in self.running_processes.items():
            # Get process info
            cmd = ' '.join(process.args)
            status = "Running" if process.poll() is None else f"Exited ({process.returncode})"
            
            print(f"{self.themes[self.theme]['info']}ID: {pid}{Style.RESET_ALL}")
            print(f"  Command: {cmd}")
            print(f"  Status: {status}")
            print()
            
        return True

    def _cmd_info(self, args: List[str]) -> bool:
        """Show information about files or directories."""
        if not args:
            print(f"{self.themes[self.theme]['error']}Error: Please specify a file or directory{Style.RESET_ALL}")
            print("Usage: info <file/dir>")
            return False
            
        path = args[0]
        if not os.path.exists(path):
            print(f"{self.themes[self.theme]['error']}Error: Path not found: {path}{Style.RESET_ALL}")
            return False
            
        try:
            # Get file/directory stats
            stats = os.stat(path)
            
            # Format times
            created = time.ctime(stats.st_ctime)
            modified = time.ctime(stats.st_mtime)
            accessed = time.ctime(stats.st_atime)
            
            # Print basic info
            print(f"\n{self.themes[self.theme]['command']}Information: {os.path.basename(path)}{Style.RESET_ALL}")
            print(f"{self.themes[self.theme]['info']}Path:{Style.RESET_ALL} {os.path.abspath(path)}")
            print(f"{self.themes[self.theme]['info']}Type:{Style.RESET_ALL} {'Directory' if os.path.isdir(path) else 'File'}")
            
            if os.path.isfile(path):
                # File-specific info
                size = os.path.getsize(path)
                print(f"{self.themes[self.theme]['info']}Size:{Style.RESET_ALL} {self._format_size(size)}")
                print(f"{self.themes[self.theme]['info']}Created:{Style.RESET_ALL} {created}")
                print(f"{self.themes[self.theme]['info']}Modified:{Style.RESET_ALL} {modified}")
                print(f"{self.themes[self.theme]['info']}Accessed:{Style.RESET_ALL} {accessed}")
                
                # Get file extension
                _, ext = os.path.splitext(path)
                if ext:
                    print(f"{self.themes[self.theme]['info']}Extension:{Style.RESET_ALL} {ext}")
                    
                # Check if text or binary
                is_text = self._is_text_file(path)
                print(f"{self.themes[self.theme]['info']}Content Type:{Style.RESET_ALL} {'Text' if is_text else 'Binary'}")
                
            else:
                # Directory-specific info
                items = os.listdir(path)
                files = [item for item in items if os.path.isfile(os.path.join(path, item))]
                dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
                
                print(f"{self.themes[self.theme]['info']}Items:{Style.RESET_ALL} {len(items)} ({len(files)} files, {len(dirs)} directories)")
                print(f"{self.themes[self.theme]['info']}Created:{Style.RESET_ALL} {created}")
                print(f"{self.themes[self.theme]['info']}Modified:{Style.RESET_ALL} {modified}")
                
            return True
            
        except Exception as e:
            print(f"{self.themes[self.theme]['error']}Error getting information: {str(e)}{Style.RESET_ALL}")
            return False

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _get_file_icon(self, ext: str) -> str:
        """Get icon for file based on extension."""
        icons = {
            '.py': "🐍",
            '.js': "📜",
            '.html': "🌐",
            '.css': "🎨",
            '.json': "📋",
            '.md': "📝",
            '.txt': "📄",
            '.pdf': "📕",
            '.jpg': "🖼️",
            '.jpeg': "🖼️",
            '.png': "🖼️",
            '.gif': "🖼️",
            '.svg': "🖼️",
            '.mp3': "🎵",
            '.mp4': "🎬",
            '.zip': "📦",
            '.tar': "📦",
            '.gz': "📦",
            '.exe': "⚙️",
            '.bat': "⚙️",
            '.sh': "⚙️",
            '.dll': "🔧",
            '.c': "📟",
            '.cpp': "📟",
            '.h': "📟",
            '.java': "☕",
            '.class': "☕",
            '.php': "🐘",
            '.rb': "💎",
            '.go': "🐹",
            '.rs': "🦀",
            '.ts': "📘",
            '.xml': "📰",
            '.yml': "📰",
            '.yaml': "📰",
            '.csv': "📊",
            '.xls': "📊",
            '.xlsx': "📊",
            '.doc': "📝",
            '.docx': "📝"
        }
        
        return icons.get(ext, "📄")

    def _is_text_file(self, filepath: str) -> bool:
        """Check if a file is a text file."""
        # Skip very large files
        if os.path.getsize(filepath) > 10_000_000:  # 10MB
            return False
            
        # Check file extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        # Known text extensions
        text_extensions = {
            '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.csv',
            '.yml', '.yaml', '.sh', '.bat', '.c', '.cpp', '.h', '.java', '.php',
            '.rb', '.go', '.rs', '.ts', '.log', '.ini', '.cfg', '.conf'
        }
        
        # Known binary extensions
        binary_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.zip',
            '.tar', '.gz', '.exe', '.dll', '.so', '.class', '.pyc', '.o'
        }
        
        # Quick check based on extension
        if ext in text_extensions:
            return True
        if ext in binary_extensions:
            return False
            
        # Check file content
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)
                # Check for null bytes (common in binary files)
                if b'\0' in chunk:
                    return False
                # Check if mostly printable ASCII
                printable = sum(c > 31 and c < 127 for c in chunk)
                return printable / len(chunk) > 0.7
        except Exception:
            return False