#!/usr/bin/env python3
"""
Kill Package for RunIT

Provides functionality to terminate processes for specific files or all RunIT processes.

Version: 1.0.0
License: MIT
"""

import os
import sys
import signal
import subprocess
import time
from typing import List, Dict, Optional, Any, Tuple

# Try to import optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed. Process detection will be limited.")
    print("Install with: pip install psutil")

# Global instance
_kill_instance = None

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function required by RunIT."""
    global _kill_instance
    if _kill_instance is None:
        _kill_instance = KillManager()
    return _kill_instance.handle_command(command, args)

class KillManager:
    """Manages process termination for RunIT."""

    def __init__(self):
        """Initialize the Kill Manager."""
        self.name = "kill_RunIT"
        self.version = "1.0.0"
        self.current_dir = os.getcwd()
        self.runit_processes = []

    def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle package commands.

        Args:
            command: The command to execute
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if command == "kill":
            return self._kill_process(args)
        return False

    def _kill_process(self, args: List[str]) -> bool:
        """Kill processes for a specific file or all RunIT processes.

        Args:
            args: Command arguments, file path or 'RunIT'

        Returns:
            bool: True if command executed successfully
        """
        if not args:
            print("Error: Please specify a file or 'RunIT'")
            print("Usage: kill <file> | kill RunIT")
            return False

        target = args[0]

        # Check if killing all RunIT processes
        if target.lower() == "runit":
            return self._kill_all_runit_processes()

        # Kill processes for a specific file
        return self._kill_file_processes(target)

    def _kill_all_runit_processes(self) -> bool:
        """Kill all RunIT processes.

        Returns:
            bool: True if command executed successfully
        """
        print("Terminating all RunIT processes...")

        if HAS_PSUTIL:
            # Use psutil for better process detection
            killed_count = 0
            current_pid = os.getpid()

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Skip current process
                    if proc.info['pid'] == current_pid:
                        continue

                    # Check if RunIT process
                    cmdline = proc.info['cmdline']
                    if cmdline and any('runit' in cmd.lower() for cmd in cmdline if cmd):
                        print(f"Terminating process {proc.info['pid']}: {' '.join(cmdline) if cmdline else proc.info['name']}")
                        proc.terminate()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            if killed_count > 0:
                print(f"Successfully terminated {killed_count} RunIT processes")
                return True
            else:
                print("No RunIT processes found")
                return True
        else:
            # Fallback method for Windows
            if os.name == 'nt':
                try:
                    # Use tasklist and taskkill
                    output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV']).decode()
                    lines = output.strip().split('\n')[1:]  # Skip header
                    
                    killed_count = 0
                    for line in lines:
                        parts = line.strip('"').split('","')
                        if len(parts) >= 2:
                            pid = parts[1]
                            # Check if RunIT process (basic check)
                            try:
                                proc_info = subprocess.check_output(['tasklist', '/FI', f'PID eq {pid}', '/V', '/FO', 'CSV']).decode()
                                if 'runit' in proc_info.lower() and str(os.getpid()) != pid:
                                    subprocess.call(['taskkill', '/F', '/PID', pid])
                                    print(f"Terminated process {pid}")
                                    killed_count += 1
                            except subprocess.CalledProcessError:
                                pass
                    
                    if killed_count > 0:
                        print(f"Successfully terminated {killed_count} RunIT processes")
                        return True
                    else:
                        print("No RunIT processes found")
                        return True
                except Exception as e:
                    print(f"Error terminating processes: {str(e)}")
                    return False
            else:
                # Fallback method for Unix-like systems
                try:
                    # Use ps and kill
                    output = subprocess.check_output(['ps', 'aux']).decode()
                    lines = output.strip().split('\n')[1:]  # Skip header
                    
                    killed_count = 0
                    current_pid = os.getpid()
                    
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            cmd = ' '.join(parts[10:])
                            
                            # Check if RunIT process (basic check)
                            if 'runit' in cmd.lower() and int(pid) != current_pid:
                                try:
                                    os.kill(int(pid), signal.SIGTERM)
                                    print(f"Terminated process {pid}: {cmd}")
                                    killed_count += 1
                                except OSError:
                                    pass
                    
                    if killed_count > 0:
                        print(f"Successfully terminated {killed_count} RunIT processes")
                        return True
                    else:
                        print("No RunIT processes found")
                        return True
                except Exception as e:
                    print(f"Error terminating processes: {str(e)}")
                    return False

    def _kill_file_processes(self, filepath: str) -> bool:
        """Kill processes for a specific file.

        Args:
            filepath: Path to the file

        Returns:
            bool: True if command executed successfully
        """
        # Normalize path
        filepath = os.path.abspath(filepath)
        
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            return False
            
        print(f"Terminating processes for file: {filepath}")
        
        if HAS_PSUTIL:
            # Use psutil for better process detection
            killed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check if process is using the file
                    cmdline = proc.info['cmdline']
                    if cmdline and any(filepath in cmd for cmd in cmdline if cmd):
                        print(f"Terminating process {proc.info['pid']}: {' '.join(cmdline) if cmdline else proc.info['name']}")
                        proc.terminate()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            # Check open files (more thorough but requires higher privileges)
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        for file in proc.open_files():
                            if file.path == filepath:
                                print(f"Terminating process {proc.pid}: {proc.name()} (has file open)")
                                proc.terminate()
                                killed_count += 1
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except Exception:
                # Open files check might fail due to permissions
                pass
                
            if killed_count > 0:
                print(f"Successfully terminated {killed_count} processes")
                return True
            else:
                print(f"No processes found for file: {filepath}")
                return True
        else:
            # Fallback method with limited functionality
            print("Limited functionality: Install psutil for better process detection")
            print("pip install psutil")
            
            # Basic check using file extension
            _, ext = os.path.splitext(filepath)
            ext = ext.lower()
            
            if ext == '.py':
                return self._kill_python_process(filepath)
            elif ext in ['.js', '.ts']:
                return self._kill_node_process(filepath)
            elif ext in ['.bat', '.cmd']:
                return self._kill_batch_process(filepath)
            else:
                print(f"Unsupported file type for basic process detection: {ext}")
                print("Install psutil for better process detection")
                return False

    def _kill_python_process(self, filepath: str) -> bool:
        """Kill Python processes running the specified file."""
        filename = os.path.basename(filepath)
        
        if os.name == 'nt':  # Windows
            try:
                # Use tasklist and taskkill
                output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV']).decode()
                lines = output.strip().split('\n')[1:]  # Skip header
                
                killed_count = 0
                for line in lines:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        pid = parts[1]
                        # Check if process is running the file (basic check)
                        try:
                            proc_info = subprocess.check_output(['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/format:csv']).decode()
                            if filename in proc_info:
                                subprocess.call(['taskkill', '/F', '/PID', pid])
                                print(f"Terminated process {pid}")
                                killed_count += 1
                        except subprocess.CalledProcessError:
                            pass
                
                if killed_count > 0:
                    print(f"Successfully terminated {killed_count} processes")
                    return True
                else:
                    print(f"No processes found for file: {filepath}")
                    return True
            except Exception as e:
                print(f"Error terminating processes: {str(e)}")
                return False
        else:  # Unix-like
            try:
                # Use ps and kill
                output = subprocess.check_output(['ps', 'aux']).decode()
                lines = output.strip().split('\n')[1:]  # Skip header
                
                killed_count = 0
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 11:
                        pid = parts[1]
                        cmd = ' '.join(parts[10:])
                        
                        # Check if process is running the file (basic check)
                        if 'python' in cmd and filename in cmd:
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"Terminated process {pid}: {cmd}")
                                killed_count += 1
                            except OSError:
                                pass
                
                if killed_count > 0:
                    print(f"Successfully terminated {killed_count} processes")
                    return True
                else:
                    print(f"No processes found for file: {filepath}")
                    return True
            except Exception as e:
                print(f"Error terminating processes: {str(e)}")
                return False

    def _kill_node_process(self, filepath: str) -> bool:
        """Kill Node.js processes running the specified file."""
        filename = os.path.basename(filepath)
        
        if os.name == 'nt':  # Windows
            try:
                # Use tasklist and taskkill
                output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq node.exe', '/FO', 'CSV']).decode()
                lines = output.strip().split('\n')[1:]  # Skip header
                
                killed_count = 0
                for line in lines:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        pid = parts[1]
                        # Check if process is running the file (basic check)
                        try:
                            proc_info = subprocess.check_output(['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/format:csv']).decode()
                            if filename in proc_info:
                                subprocess.call(['taskkill', '/F', '/PID', pid])
                                print(f"Terminated process {pid}")
                                killed_count += 1
                        except subprocess.CalledProcessError:
                            pass
                
                if killed_count > 0:
                    print(f"Successfully terminated {killed_count} processes")
                    return True
                else:
                    print(f"No processes found for file: {filepath}")
                    return True
            except Exception as e:
                print(f"Error terminating processes: {str(e)}")
                return False
        else:  # Unix-like
            try:
                # Use ps and kill
                output = subprocess.check_output(['ps', 'aux']).decode()
                lines = output.strip().split('\n')[1:]  # Skip header
                
                killed_count = 0
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 11:
                        pid = parts[1]
                        cmd = ' '.join(parts[10:])
                        
                        # Check if process is running the file (basic check)
                        if 'node' in cmd and filename in cmd:
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"Terminated process {pid}: {cmd}")
                                killed_count += 1
                            except OSError:
                                pass
                
                if killed_count > 0:
                    print(f"Successfully terminated {killed_count} processes")
                    return True
                else:
                    print(f"No processes found for file: {filepath}")
                    return True
            except Exception as e:
                print(f"Error terminating processes: {str(e)}")
                return False

    def _kill_batch_process(self, filepath: str) -> bool:
        """Kill batch processes running the specified file."""
        filename = os.path.basename(filepath)
        
        if os.name == 'nt':  # Windows
            try:
                # Use tasklist and taskkill
                output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FO', 'CSV']).decode()
                lines = output.strip().split('\n')[1:]  # Skip header
                
                killed_count = 0
                for line in lines:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        pid = parts[1]
                        # Check if process is running the file (basic check)
                        try:
                            proc_info = subprocess.check_output(['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/format:csv']).decode()
                            if filename in proc_info:
                                subprocess.call(['taskkill', '/F', '/PID', pid])
                                print(f"Terminated process {pid}")
                                killed_count += 1
                        except subprocess.CalledProcessError:
                            pass
                
                if killed_count > 0:
                    print(f"Successfully terminated {killed_count} processes")
                    return True
                else:
                    print(f"No processes found for file: {filepath}")
                    return True
            except Exception as e:
                print(f"Error terminating processes: {str(e)}")
                return False
        else:
            print("Batch file process detection not supported on this platform")
            return False