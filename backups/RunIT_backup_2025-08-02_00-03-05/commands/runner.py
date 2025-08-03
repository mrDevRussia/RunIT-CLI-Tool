"""
File Runner Module for RunIT CLI Tool.
Handles execution of various file types with appropriate interpreters.
"""

import os
import subprocess
import sys
from pathlib import Path
from utils.file_utils import FileUtils
from utils.lang_utils import LanguageUtils
from utils.logger import Logger


class FileRunner:
    """
    Handles running files with auto-detection of file extensions
    and appropriate interpreter selection.
    """

    def __init__(self):
        """Initialize the FileRunner with utilities."""
        self.file_utils = FileUtils()
        self.lang_utils = LanguageUtils()
        self.logger = Logger()

    def get_interpreter_command(self, file_path):
        """
        Get the appropriate interpreter command for a file.
        
        Args:
            file_path (Path): Path object of the file
            
        Returns:
            list: Command list for subprocess, or None if unsupported
        """
        extension = file_path.suffix.lower()
        
        interpreter_map = {
            '.py': ['python'],
            '.js': ['node'],
            '.html': ['start'],  # Windows default browser
            '.css': ['start'],   # Windows default program
            '.php': ['php'],
            '.bat': [],          # Run directly
            '.cmd': [],          # Run directly
            '.sh': ['bash'],     # If available on Windows
            '.c': None,          # Needs compilation
            '.cpp': None,        # Needs compilation
            '.java': None,       # Needs compilation
            '.ts': ['ts-node'],  # If available
            '.json': ['start'],  # Windows default program
            '.xml': ['start'],   # Windows default program
            '.txt': ['start']    # Windows default program
        }
        
        if extension in interpreter_map:
            command = interpreter_map[extension]
            if command is None:
                return None  # Compilation required
            elif command == []:
                return [str(file_path)]  # Direct execution
            else:
                return command + [str(file_path)]
        
        return None

    def check_interpreter_availability(self, interpreter):
        """
        Check if an interpreter is available on the system.
        
        Args:
            interpreter (str): Name of the interpreter
            
        Returns:
            bool: True if available, False otherwise
        """
        try:
            # Try to run the interpreter with --version or -v
            result = subprocess.run(
                [interpreter, '--version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            try:
                # Try alternative version flag
                result = subprocess.run(
                    [interpreter, '-v'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                return False

    def handle_compilation_required(self, file_path):
        """
        Handle files that require compilation before execution.
        
        Args:
            file_path (Path): Path to the file
        """
        extension = file_path.suffix.lower()
        
        compilation_info = {
            '.c': {
                'compiler': 'gcc',
                'command': f'gcc "{file_path}" -o "{file_path.stem}.exe"',
                'run_command': f'"{file_path.stem}.exe"'
            },
            '.cpp': {
                'compiler': 'g++',
                'command': f'g++ "{file_path}" -o "{file_path.stem}.exe"',
                'run_command': f'"{file_path.stem}.exe"'
            },
            '.java': {
                'compiler': 'javac',
                'command': f'javac "{file_path}"',
                'run_command': f'java "{file_path.stem}"'
            }
        }
        
        if extension in compilation_info:
            info = compilation_info[extension]
            print(f"⚠️  File '{file_path.name}' requires compilation first.")
            print(f"Compiler needed: {info['compiler']}")
            print(f"Compile with: {info['command']}")
            print(f"Then run with: {info['run_command']}")
            
            # Check if compiler is available
            if self.check_interpreter_availability(info['compiler']):
                response = input("Would you like to compile and run now? (y/n): ").lower()
                if response in ['y', 'yes']:
                    self.compile_and_run(file_path, info)
            else:
                print(f"❌ Compiler '{info['compiler']}' not found on system.")

    def compile_and_run(self, file_path, compilation_info):
        """
        Compile and run a file that requires compilation.
        
        Args:
            file_path (Path): Path to the source file
            compilation_info (dict): Compilation information
        """
        try:
            print(f"🔨 Compiling {file_path.name}...")
            
            # Run compilation command
            compile_result = subprocess.run(
                compilation_info['command'],
                shell=True,
                capture_output=True,
                text=True,
                cwd=file_path.parent
            )
            
            if compile_result.returncode == 0:
                print("✅ Compilation successful!")
                print(f"🚀 Running compiled program...")
                
                # Run the compiled program
                run_result = subprocess.run(
                    compilation_info['run_command'],
                    shell=True,
                    cwd=file_path.parent
                )
                
                if run_result.returncode == 0:
                    print("✅ Program executed successfully!")
                else:
                    print(f"❌ Program execution failed with code {run_result.returncode}")
                    
            else:
                print("❌ Compilation failed!")
                if compile_result.stderr:
                    print("Compilation errors:")
                    print(compile_result.stderr)
                    
        except Exception as e:
            self.logger.error(f"Error during compilation: {e}")
            print(f"❌ Compilation error: {e}")

    def run_file(self, filename):
        """
        Main method to run a file with appropriate interpreter.
        
        Args:
            filename (str): Name or path of the file to run
        """
        try:
            # Convert to Path object and resolve
            file_path = Path(filename).resolve()
            
            # Check if file exists
            if not file_path.exists():
                print(f"❌ File not found: {filename}")
                return
            
            # Check if it's actually a file
            if not file_path.is_file():
                print(f"❌ '{filename}' is not a file")
                return
            
            # Get file info for logging
            file_size = self.file_utils.get_file_size(file_path)
            self.logger.info(f"Running file: {file_path} ({file_size})")
            
            # Get interpreter command
            command = self.get_interpreter_command(file_path)
            
            if command is None:
                self.handle_compilation_required(file_path)
                return
            
            # Check if interpreter is available (except for direct execution)
            if len(command) > 1:  # Has interpreter
                interpreter = command[0]
                if not self.check_interpreter_availability(interpreter):
                    if file_path.suffix.lower() == '.html':
                        print("ℹ️ HTML files can be viewed using the 'preview' command and modified using the 'edit' command.")
                    else:
                        print(f"❌ Interpreter '{interpreter}' not found on system.")
                        print(f"Please install {interpreter} to run {file_path.suffix} files.")
                    return
            
            print(f"🚀 Running {file_path.name}...")
            print("-" * 50)
            
            # Execute the file
            if command[0] == 'start':
                # Use Windows start command for default program association
                subprocess.run(command + [str(file_path)], shell=True)
                print(f"✅ Opened {file_path.name} with default program")
            else:
                # Run with specific interpreter or directly
                result = subprocess.run(
                    command,
                    cwd=file_path.parent,
                    shell=(len(command) == 1)  # Use shell for direct execution
                )
                
                print("-" * 50)
                if result.returncode == 0:
                    print(f"✅ {file_path.name} executed successfully!")
                else:
                    print(f"❌ {file_path.name} execution failed with code {result.returncode}")
            
            self.logger.info(f"File execution completed: {file_path}")
            
        except KeyboardInterrupt:
            print("\n⚠️  Execution interrupted by user")
        except Exception as e:
            self.logger.error(f"Error running file {filename}: {e}")
            print(f"❌ Error running file: {e}")

    def list_supported_extensions(self):
        """
        Return a list of supported file extensions.
        
        Returns:
            list: List of supported extensions
        """
        return ['.py', '.js', '.html', '.css', '.php', '.bat', '.cmd', '.sh', 
                '.c', '.cpp', '.java', '.ts', '.json', '.xml', '.txt']
