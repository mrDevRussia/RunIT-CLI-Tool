#!/usr/bin/env python3
"""
RunIT - Smart Terminal Assistant for Windows
A professional CLI tool for running, creating, and analyzing code files.

Author: RunIT Development Team
Version: 1.3.0
License: MIT
"""

import sys
import os
import shlex
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commands.runner import FileRunner
from commands.creator import FileCreator
from commands.scanner import VirusScanner
from commands.searcher import FileSearcher
from commands.info import FileInfo
from commands.helper import HelpDisplay
from commands.ai_assistant import AIAssistant
from commands.package_manager import PackageManager
from commands.file_manager import FileManager
from commands.deployer import Deployer
from commands.converter import Converter
from utils.logger import Logger


class RunITCLI:
    """
    Main CLI interface for RunIT tool.
    Provides a REPL-like experience for Windows CMD.
    """

    def __init__(self):
        """Initialize the RunIT CLI with all command handlers."""
        self.logger = Logger()
        self.runner = FileRunner()
        self.creator = FileCreator()
        self.scanner = VirusScanner()
        self.searcher = FileSearcher()
        self.info = FileInfo()
        self.helper = HelpDisplay()
        self.ai_assistant = AIAssistant()
        self.package_manager = PackageManager()
        self.file_manager = FileManager()
        self.deployer = Deployer()
        self.converter = Converter()
        self.running = True
        
        # Initialize commands dictionary
        self.commands = {
            'run': self.cmd_run,
            'create': self.cmd_create,
            'search': self.cmd_search,
            'scan': self.cmd_scan,
            'info': self.cmd_info,
            'help': self.cmd_help,
            'runai': self.cmd_runai,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            # New v1.1 commands
            'install': self.cmd_install,
            'update': self.cmd_update,
            'show': self.cmd_show,
            'edit': self.cmd_edit,
            'go': self.cmd_go,
            'version': self.cmd_version,
            'test': self.cmd_test,
            # Package commands (when packages are installed)
            'preview': self.cmd_preview,
            # Website deployment commands new v1.2.0 commands
            'deploy': self.cmd_deploy,
            'stopdeploy': self.cmd_stopdeploy,
            'share': self.cmd_share,
            'setport': lambda args: self.deployer.set_port(int(args[0])) if args and args[0].isdigit() else print("❌ Please provide a valid port number (e.g. 'setport 8080')"),
            'convert': self.cmd_convert,
            # New v1.3.0 commands
            'restart': self.cmd_restart,
            'uninstall': self.cmd_uninstall,
            'adm': self.cmd_adm,
            'kill': self.cmd_kill,
        }
        
        # Load package commands
        self._load_package_commands()

    def _load_package_commands(self):
        """Load commands from installed packages."""
        installed_packages = self.package_manager.get_installed_packages()
        for package_name, package_info in installed_packages.items():
            if package_info['installed'] and package_info['install_path']:
                try:
                    # Get absolute package path
                    package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), package_info['install_path']))
                    self.logger.info(f"Loading package {package_name} from {package_path}")
                    
                    # Add package path to sys.path if not already present
                    if package_path not in sys.path:
                        sys.path.insert(0, package_path)
                        self.logger.info(f"Added {package_path} to sys.path")
                    
                    # Print current sys.path for debugging
                    self.logger.info(f"Current sys.path: {sys.path}")
                    
                    # Print current working directory
                    self.logger.info(f"Current working directory: {os.getcwd()}")
                    
                    # Get module name without .py extension
                    module_name = package_info['main_file'].replace('.py', '')
                    self.logger.info(f"Importing module {module_name}")
                    
                    # Remove module from sys.modules if already imported
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                        self.logger.info(f"Removed {module_name} from sys.modules")
                    
                    # Import the module
                    try:
                        package_module = __import__(module_name)
                        self.logger.info(f"Successfully imported {module_name}")
                        self.logger.info(f"Module attributes: {dir(package_module)}")
                    except ImportError as e:
                        self.logger.error(f"Failed to import {module_name}: {str(e)}")
                        continue
                    
                    # Check if module has handle_command function
                    if hasattr(package_module, 'handle_command'):
                        self.logger.info(f"Found handle_command in {module_name}: {getattr(package_module, 'handle_command')}")
                        self.logger.info(f"Found handle_command in {module_name}")
                        # Load package info
                        package_info_path = os.path.join(package_path, 'package_info.json')
                        if os.path.exists(package_info_path):
                            with open(package_info_path) as f:
                                pkg_info = json.load(f)
                                self.logger.info(f"Loaded package info from {package_info_path}")
                                
                                # Register each command from package_info.json
                                for cmd_name in pkg_info.get('commands', {}).keys():
                                    # Create a closure to capture command name and module
                                    def create_handler(cmd, mod):
                                        def handler(args):
                                            try:
                                                return mod.handle_command(cmd, args)
                                            except Exception as e:
                                                self.logger.error(f"Error executing command {cmd}: {str(e)}")
                                                return False
                                        return handler
                                    
                                    # Register command handler
                                    self.commands[cmd_name] = create_handler(cmd_name, package_module)
                                    self.logger.info(f"Registered command: {cmd_name}")

                                    self.logger.info(f"Registered command '{cmd_name}' from package {package_name}")
                        else:
                            self.logger.error(f"Package info file not found: {package_info_path}")
                    else:
                        self.logger.error(f"Module {module_name} does not have handle_command function")
                except Exception as e:
                    self.logger.error(f"Failed to load package {package_name}: {str(e)}")

    def cmd_convert(self, args):
        """Convert source code between different programming languages."""
        if len(args) != 2:
            self.logger.error("Invalid arguments for convert command")
            print("❌ Usage: convert <source_file> <target_language>")
            print("Supported conversions:")
            for conversion, details in self.converter.get_supported_conversions().items():
                source, target = details
                print(f"  • {source} → {target}")
            return

        source_file = args[0]
        target_language = args[1].lower()

        if not os.path.exists(source_file):
            self.logger.error(f"Source file not found: {source_file}")
            print(f"❌ Source file '{source_file}' not found")
            return

        converted_code = self.converter.convert_code(source_file, target_language)
        if converted_code:
            # Map target language to correct file extension
            ext_map = {
                'python': 'py',
                'javascript': 'js',
                'markdown': 'md'
            }
            target_ext = ext_map.get(target_language, target_language)
            output_file = f"{os.path.splitext(source_file)[0]}.{target_ext}"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(converted_code)
                self.logger.info(f"Successfully converted {source_file} to {target_language}")
                print(f"✅ Code converted successfully! Output saved to: {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to save converted code: {str(e)}")
                print(f"❌ Error saving converted code: {str(e)}")
        else:
            self.logger.error(f"Code conversion failed for {source_file} to {target_language}")
            print("❌ Code conversion failed. Please check the supported conversions and try again.")


    def display_banner(self):
        """Display the RunIT welcome banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                         RunIT v1.3.0                         ║
║              Smart Terminal Assistant for Windows            ║
║                Your assistant between your hands             ║
╠══════════════════════════════════════════════════════════════╣
║     Type 'help' for commands | Type 'version' for packages   ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
        self.logger.info("RunIT CLI started successfully")

    def parse_command(self, input_line):
        """
        Parse user input into command and arguments.
        
        Args:
            input_line (str): Raw user input
            
        Returns:
            tuple: (command, args_list)
        """
        try:
            # Use shlex to properly handle quoted arguments
            parts = shlex.split(input_line.strip())
            if not parts:
                return None, []
            
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            return command, args
        except ValueError as e:
            self.logger.error(f"Invalid command syntax: {e}")
            return None, []

    def cmd_run(self, args):
        """Handle 'run' command to execute files."""
        if not args:
            print("❌ Error: Please specify a filename to run")
            print("Usage: run <filename>")
            return
        
        filename = args[0]
        self.runner.run_file(filename)

    def cmd_create(self, args):
        """Handle 'create' command to create new files."""
        if len(args) < 2:
            print("❌ Error: Please specify language and filename")
            print("Usage: create <language> <filename>")
            return
        
        language = args[0].lower()
        filename = args[1]
        self.creator.create_file(language, filename)

    def cmd_search(self, args):
        """Handle 'search' command to find keywords in files."""
        if len(args) < 2:
            print("❌ Error: Please specify keyword and filename")
            print("Usage: search <keyword> <filename>")
            return
        
        keyword = args[0]
        filename = args[1]
        self.searcher.search_in_file(keyword, filename)

    def cmd_scan(self, args):
        """Handle 'scan' command for virus detection."""
        if not args:
            print("❌ Error: Please specify a filename to scan")
            print("Usage: scan <filename>")
            return
        
        filename = args[0]
        self.scanner.scan_file(filename)

    def cmd_info(self, args):
        """Handle 'info' command to display file information."""
        if not args:
            print("❌ Error: Please specify a filename")
            print("Usage: info <filename>")
            return
        
        filename = args[0]
        self.info.show_file_info(filename)

    def cmd_help(self, args):
        """Handle 'help' command to show usage information."""
        if args and args[0] in self.commands:
            # Show specific command help
            if args[0] == 'runai':
                self.ai_assistant.show_ai_help()
            else:
                self.helper.show_command_help(args[0])
        else:
            # Show general help
            self.helper.show_general_help()

    def cmd_runai(self, args):
        """Handle 'runai' command for AI assistance."""
        if not args:
            print("❌ Error: Please provide a question or topic")
            print("Usage: runai <question>")
            print("Example: runai How do I create a function in Python?")
            print("Example: runai file:example.py")
            return
        
        # Join all arguments to form the query
        query = ' '.join(args)
        
        # Check if it's a file analysis request
        if query.startswith('file:'):
            filename = query[5:].strip()
            self.ai_assistant.help_with_file(filename)
        else:
            # General AI assistance
            response = self.ai_assistant.get_code_assistance(query)
            self.ai_assistant.format_ai_response(response)
            
    def cmd_deploy(self, args):
        """Handle 'deploy' command to start a local server for static websites."""
        if not args:
            print("❌ Error: Please specify a folder to deploy")
            print("Usage: deploy <folder>")
            print("Example: deploy website")
            return
        
        folder_path = args[0]
        if not os.path.isdir(folder_path):
            print(f"❌ Error: '{folder_path}' is not a valid directory")
            return
            
        self.deployer.deploy_site(folder_path)

    def cmd_stopdeploy(self, args):
        """Handle 'stopdeploy' command to stop the local server."""
        self.deployer.stop_deployment()
        
    def cmd_share(self, args):
        """Handle 'share' command to generate a public URL for the deployed site."""
        self.deployer.generate_public_url()

    def cmd_clear(self, args):
        """Handle 'clear' command to clear the terminal."""
        os.system('cls')  # Windows CMD clear command
        self.display_banner()

    def cmd_exit(self, args):
        """Handle 'exit' command to quit the application."""
        print("👋 Thanks for using RunIT! Goodbye!")
        self.logger.info("RunIT CLI session ended")
        self.running = False

    # New v1.1 commands
    def cmd_install(self, args):
        """Install a package from GitHub repository."""
        if not args:
            print("❌ Please specify a package to install")
            print("Usage: install <package_name>")
            return
            
        package_name = args[0]
        print(f"📦 Installing package {package_name}...")
        
        if self.package_manager.install_package(package_name):
            print(f"✅ Successfully installed {package_name}")
        else:
            print(f"❌ Failed to install {package_name}. Check logs for details.")

    def cmd_update(self, args):
        """Handle 'update' command to update packages or the tool."""
        if not args:
            print("❌ Error: Please specify what to update")
            print("Usage: update <package_name@latest> or update RunIT@latest")
            return
        
        package_name = args[0]
        self.package_manager.update_package(package_name)

    def cmd_show(self, args):
        """Handle 'show' command to display file structures."""
        if not args:
            print("❌ Error: Please specify a file or directory to show")
            print("Usage: show <filename_or_directory>")
            return
        
        filepath = args[0]
        self.file_manager.show_file_structure(filepath)

    def cmd_edit(self, args):
        """Handle 'edit' command to edit files."""
        if not args:
            print("❌ Error: Please specify a file to edit")
            print("Usage: edit <filename> [editor]")
            return
        
        filepath = args[0]
        editor = args[1] if len(args) > 1 else None
        self.file_manager.edit_file(filepath, editor)

    def cmd_go(self, args):
        """Handle 'go' command to navigate to directories."""
        if not args:
            print("❌ Error: Please specify a directory path")
            print("Usage: go <directory_path>")
            return
        
        directory_path = args[0]
        self.file_manager.go_to_directory(directory_path)

    def cmd_version(self, args):
        """Handle 'version' command to show tool version."""
        version = self.package_manager.get_version()
        print(f"🚀 RunIT CLI Tool Version {version}")
        print("Smart Terminal Assistant for Windows")
        
        # Show package information
        print("\n📦 Package Status:")
        self.package_manager.list_packages()

    def cmd_test(self, args):
        """Handle 'test' command to test tool functionality."""
        print("🧪 Testing RunIT functionality...")
        print("="*40)
        
        # Test core system
        print("✅ Core CLI system: OK")
        
        # Test package system
        if self.package_manager.test_installation():
            print("✅ Package system: OK")
        else:
            print("❌ Package system: FAILED")
        
        # Test file system access
        try:
            current_dir = self.file_manager.get_current_directory()
            print(f"✅ File system access: OK (Current: {current_dir})")
        except Exception as e:
            print(f"❌ File system access: FAILED ({e})")
        
        print("🎉 RunIT test completed!")

    def cmd_preview(self, args):
        """Handle 'preview' command (requires preview_RunIT package)."""
        if not args:
            print("❌ Error: Please specify an HTML file to preview")
            print("Usage: preview <filename.html>")
            return
        
        # Check if preview package is installed
        try:
            sys.path.insert(0, str(Path("packages/preview_RunIT")))
            import importlib.util
            spec = importlib.util.spec_from_file_location("preview", Path("packages/preview_RunIT/preview.py"))
            if spec and spec.loader:
                preview_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(preview_module)
                preview_module.main(args)
            else:
                raise ImportError("Preview module not found")
        except Exception as e:
            print("❌ Preview package not installed or not working")
            print("   Install it with: install preview_RunIT@latest")
            self.logger.error(f"Preview command failed: {e}")
            
    def cmd_restart(self, args):
        """Restart the RunIT tool."""
        self.logger.info("Restarting RunIT...")
        print("🔄 Restarting RunIT...")
        
        # Get the current executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            executable = sys.executable
        else:
            # Running as script
            executable = sys.executable
            script = os.path.abspath(__file__)
        
        # Close current instance
        self.running = False
        
        # Start new process using subprocess instead of os.execl to handle paths with spaces
        try:
            import subprocess
            if getattr(sys, 'frozen', False):
                subprocess.Popen([executable] + sys.argv)
            else:
                subprocess.Popen([executable, script] + sys.argv[1:])
            # Exit the current process
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Failed to restart: {str(e)}")
            print(f"❌ Failed to restart: {str(e)}")
            # Restart running to keep current instance alive
            self.running = True
            return False
        
        return True
    
    def cmd_uninstall(self, args):
        """Uninstall the RunIT tool."""
        self.logger.info("Uninstalling RunIT...")
        print("⚠️ Are you sure you want to uninstall RunIT? This will remove all files and settings.")
        print("   Type 'yes' to confirm or anything else to cancel:")
        
        confirmation = input("> ").strip().lower()
        if confirmation != "yes":
            print("✅ Uninstallation cancelled.")
            return False
        
        print("🗑️ Uninstalling RunIT...")
        
        # Get the installation directory (parent of current file)
        install_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create uninstall script
        try:
            # Create a batch file to delete the installation directory after this process exits
            uninstall_script = os.path.join(os.environ.get('TEMP', '.'), 'uninstall_runit.bat')
            with open(uninstall_script, 'w') as f:
                f.write("@echo off\n")
                f.write("echo Removing RunIT files...\n")
                f.write(f"timeout /t 2 /nobreak > nul\n")
                f.write(f"rmdir /s /q \"{install_dir}\"\n")
                f.write("echo RunIT has been uninstalled.\n")
                f.write("echo Thank you for using RunIT!\n")
                f.write("pause\n")
                f.write(f"del \"{uninstall_script}\"\n")
            
            # Execute the uninstall script and exit
            print("✅ RunIT will be uninstalled after you close this window.")
            print("   Thank you for using RunIT!")
            
            # Start the uninstall script in a new process
            import subprocess
            subprocess.Popen(['cmd', '/c', uninstall_script], 
                            shell=True, 
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Exit the current process
            self.running = False
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall: {str(e)}")
            print(f"❌ Failed to uninstall: {str(e)}")
            return False
    
    def cmd_adm(self, args):
        """Advanced Developer Mode - delegates to IDER package."""
        # Check if IDER package is installed
        if not self.package_manager.is_package_installed("IDER_RunIT"):
            self.logger.error("IDER package not installed")
            print("❌ Advanced Developer Mode requires the IDER package.")
            print("   Run: install IDER")
            return False
            
        # The actual implementation will be handled by the IDER package
        # through the package command handler mechanism
        return False  # Return False to let the package handler take over
        
    def cmd_kill(self, args):
        """Kill command handler - delegates to kill package."""
        # Check if kill package is installed
        if not self.package_manager.is_package_installed("kill_RunIT"):
            self.logger.error("Kill package not installed")
            print("❌ Process termination requires the kill package.")
            print("   Run: install kill")
            return False
            
        # The actual implementation will be handled by the kill package
        # through the package command handler mechanism
        return False  # Return False to let the package handler take over

    def run_command(self, command, args):
        """
        Execute a command with given arguments.
        
        Args:
            command (str): Command name
            args (list): Command arguments
        """
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                self.logger.error(f"Error executing command '{command}': {e}")
                print(f"❌ An error occurred while executing '{command}': {e}")
        else:
            print(f"❌ Unknown command: '{command}'")
            print("Type 'help' to see available commands")

    def run(self):
        """Main REPL loop for the CLI interface."""
        self.display_banner()
        
        while self.running:
            try:
                # Show prompt and get user input
                user_input = input("RunIT> ").strip()
                
                # Skip empty inputs
                if not user_input:
                    continue
                    
                # Parse and execute command
                command, args = self.parse_command(user_input)
                if command:
                    self.run_command(command, args)
                    
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user. Goodbye!")
                self.logger.info("RunIT CLI interrupted by user")
                break
            except EOFError:
                print("\n👋 Session ended. Goodbye!")
                self.logger.info("RunIT CLI session ended via EOF")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in main loop: {e}")
                print(f"❌ An unexpected error occurred: {e}")


def main():
    """Entry point for the RunIT CLI application."""
    try:
        # Handle command line arguments
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            if arg in ['--help', '-h', 'help']:
                show_help()
                return
            elif arg in ['--version', '-v', 'version']:
                show_version()
                return
            elif arg == 'test':
                run_self_test()
                return
            elif arg == 'clean':
                clean_cache()
                return
        
        # Check if running on Windows (with development override)
        if os.name != 'nt':
            # Allow running in development/testing environments
            dev_mode = os.environ.get('RUNIT_DEV_MODE', 'false').lower() == 'true'
            if not dev_mode:
                print("❌ RunIT is designed specifically for Windows systems.")
                print("Please run this tool on a Windows machine with CMD or PowerShell.")
                print("💡 For development/testing, set RUNIT_DEV_MODE=true environment variable.")
                sys.exit(1)
            else:
                print("🔧 Development Mode: Running RunIT on non-Windows system for testing")
        
        # Initialize and run the CLI
        cli = RunITCLI()
        cli.run()
        
    except Exception as e:
        print(f"❌ Failed to start RunIT: {e}")
        sys.exit(1)

def show_help():
    """Show command line help."""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║                     RunIT CLI Tool v1.3.0                    ║
║              Smart Terminal Assistant for Windows            ║
╚══════════════════════════════════════════════════════════════╝

USAGE:
  python main.py [options]
  RunIT.bat [options]

OPTIONS:
  --help, -h      Show this help message
  --version, -v   Show version information
  test           Run self-test to verify installation
  clean          Clean cache and temporary files

INTERACTIVE MODE:
  Running without arguments starts the interactive REPL mode.
  
COMMANDS (in interactive mode):
  run <file>              Execute a file with auto-detection
  create <lang> <file>    Create a new file with boilerplate
  search <keyword> <file> Search for keywords in files  
  scan <file>             Scan file for suspicious patterns
  info <file>             Show comprehensive file information
  help [command]          Show help for commands
  clear                   Clear the terminal
  deploy <folder>         Deploy a static website from the specified folder
  stopdeploy              Stop any running deployment servers
  share                   Generate a public URL for the deployed site
  setport <number>        Change the deployment port (e.g. 'setport 8080')
  restart                 Restart the RunIT tool
  uninstall               Uninstall the RunIT tool
  adm                     Enter Advanced Developer Mode
  kill <file>             Terminate processes for a specific file
  kill RunIT              Terminate all RunIT processes

Note: If you encounter 'Port is already in use' error:
1. Try running 'stopdeploy' command first
2. Or change the port using 'setport <number>' command
3. Then try deploying again
  exit, quit              Exit RunIT

EXAMPLES:
  RunIT.bat                     # Start interactive mode
  RunIT.bat help                # Show this help
  RunIT.bat test                # Test installation
  
For detailed documentation, see docs/README.md
"""
    print(help_text)

def show_version():
    """Show version information."""
    print("RunIT CLI Tool v1.3.0")
    print("Copyright (c) 2025 RunIT Development Team")
    print("License: MIT")
    
def run_self_test():
    """Run comprehensive self-test."""
    print("🧪 Running RunIT Self-Test...")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Core imports
    try:
        from commands.runner import FileRunner
        from commands.creator import FileCreator
        from commands.scanner import VirusScanner
        from commands.searcher import FileSearcher
        from commands.info import FileInfo
        from commands.helper import HelpDisplay
        print("✅ Core modules import successful")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Core modules import failed: {e}")
        test_results.append(False)
    
    # Test 2: Utilities
    try:
        from utils.file_utils import FileUtils
        from utils.lang_utils import LanguageUtils
        from utils.logger import Logger
        print("✅ Utility modules import successful")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Utility modules import failed: {e}")
        test_results.append(False)
    
    # Test 3: Directory structure
    required_dirs = ['temp', 'cache', 'logs', 'samples']
    dirs_ok = True
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"⚠️ Directory '{dir_name}' not found")
            dirs_ok = False
    if dirs_ok:
        print("✅ Directory structure verified")
        test_results.append(True)
    else:
        test_results.append(False)
    
    # Test 4: Sample files
    sample_files = ['samples/hello.py', 'samples/hello.js', 'samples/test.html', 'samples/test.bat']
    samples_ok = True
    for sample in sample_files:
        if not os.path.exists(sample):
            print(f"⚠️ Sample file '{sample}' not found")
            samples_ok = False
    if samples_ok:
        print("✅ Sample files verified")
        test_results.append(True)
    else:
        test_results.append(False)
    
    # Test 5: Python execution
    try:
        import subprocess
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python execution verified: {result.stdout.strip()}")
            test_results.append(True)
        else:
            print("❌ Python execution failed")
            test_results.append(False)
    except Exception as e:
        print(f"❌ Python execution test failed: {e}")
        test_results.append(False)
    
    # Final results
    print("=" * 50)
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print("🎉 All tests passed! RunIT is ready for use.")
        print("Start with: python main.py  or  RunIT.bat")
    else:
        print(f"⚠️ {passed}/{total} tests passed. Some features may not work correctly.")
        print("Consider re-running setup.bat")

def clean_cache():
    """Clean cache and temporary files."""
    print("🧹 Cleaning RunIT cache and temporary files...")
    
    import shutil
    cleaned = []
    
    # Clean cache directory
    if os.path.exists('cache'):
        try:
            shutil.rmtree('cache')
            os.makedirs('cache')
            cleaned.append('cache/')
        except Exception as e:
            print(f"⚠️ Could not clean cache: {e}")
    
    # Clean temp directory
    if os.path.exists('temp'):
        try:
            shutil.rmtree('temp')
            os.makedirs('temp')
            cleaned.append('temp/')
        except Exception as e:
            print(f"⚠️ Could not clean temp: {e}")
    
    # Clean log files older than 7 days
    if os.path.exists('logs'):
        try:
            import glob
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=7)
            log_files = glob.glob('logs/*.log')
            for log_file in log_files:
                if os.path.getmtime(log_file) < cutoff.timestamp():
                    os.remove(log_file)
                    cleaned.append(f'old log: {os.path.basename(log_file)}')
        except Exception as e:
            print(f"⚠️ Could not clean old logs: {e}")
    
    if cleaned:
        print(f"✅ Cleaned: {', '.join(cleaned)}")
    else:
        print("✅ No cleanup needed")
    
    print("Cache cleanup completed.")


if __name__ == "__main__":
    main()
