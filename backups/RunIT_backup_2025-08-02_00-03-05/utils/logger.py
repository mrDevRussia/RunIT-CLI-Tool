"""
Logger Module for RunIT CLI Tool.
Provides structured logging capabilities with different levels and file output.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path


class Logger:
    """
    Centralized logging utility for RunIT CLI tool.
    Provides structured logging with different levels and optional file output.
    """

    def __init__(self, name='RunIT', log_level='INFO', log_to_file=True, log_dir='logs'):
        """
        Initialize the logger.
        
        Args:
            name (str): Logger name
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file (bool): Whether to log to file
            log_dir (str): Directory for log files
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_to_file = log_to_file
        self.log_dir = Path(log_dir)
        
        # Create logger instance
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_logger()

    def _setup_logger(self):
        """Set up logger with appropriate handlers and formatters."""
        
        # Create formatter for detailed logging
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create formatter for console (simpler)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Set up file handler if requested
        if self.log_to_file:
            try:
                # Create log directory if it doesn't exist
                self.log_dir.mkdir(exist_ok=True)
                
                # Create log filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d')
                log_filename = f'runit_{timestamp}.log'
                log_filepath = self.log_dir / log_filename
                
                # Create file handler
                file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)  # Log everything to file
                file_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(file_handler)
                
                # Store log file path for reference
                self.log_file_path = log_filepath
                
            except (OSError, IOError) as e:
                # If we can't create log file, continue without file logging
                print(f"Warning: Could not set up file logging: {e}")
                self.log_to_file = False
        
        # Set up console handler for errors and warnings only (optional)
        # Uncomment below if you want console logging in addition to file logging
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        """

    def debug(self, message, *args, **kwargs):
        """
        Log debug message.
        
        Args:
            message (str): Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """
        Log info message.
        
        Args:
            message (str): Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """
        Log warning message.
        
        Args:
            message (str): Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """
        Log error message.
        
        Args:
            message (str): Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """
        Log critical message.
        
        Args:
            message (str): Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        """
        Log exception with traceback.
        
        Args:
            message (str): Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        self.logger.exception(message, *args, **kwargs)

    def log_command_execution(self, command, args, result=None, error=None):
        """
        Log command execution details.
        
        Args:
            command (str): Command name
            args (list): Command arguments
            result (any): Command result
            error (Exception): Exception if command failed
        """
        args_str = ' '.join(str(arg) for arg in args) if args else 'None'
        
        if error:
            self.error(f"Command '{command}' failed | Args: {args_str} | Error: {error}")
        else:
            self.info(f"Command '{command}' executed | Args: {args_str}")

    def log_file_operation(self, operation, file_path, success=True, details=None):
        """
        Log file operation details.
        
        Args:
            operation (str): Type of operation (create, read, write, delete, etc.)
            file_path (str or Path): Path to the file
            success (bool): Whether operation was successful
            details (str): Additional details about the operation
        """
        status = "SUCCESS" if success else "FAILED"
        details_str = f" | Details: {details}" if details else ""
        
        log_message = f"File {operation} {status} | Path: {file_path}{details_str}"
        
        if success:
            self.info(log_message)
        else:
            self.error(log_message)

    def log_security_event(self, event_type, file_path, severity='INFO', details=None):
        """
        Log security-related events (virus scans, suspicious patterns, etc.).
        
        Args:
            event_type (str): Type of security event
            file_path (str or Path): File being scanned/analyzed
            severity (str): Severity level (INFO, WARNING, ERROR, CRITICAL)
            details (str): Additional details about the event
        """
        details_str = f" | Details: {details}" if details else ""
        message = f"Security Event: {event_type} | File: {file_path}{details_str}"
        
        severity_level = severity.upper()
        if severity_level == 'DEBUG':
            self.debug(message)
        elif severity_level == 'INFO':
            self.info(message)
        elif severity_level == 'WARNING':
            self.warning(message)
        elif severity_level == 'ERROR':
            self.error(message)
        elif severity_level == 'CRITICAL':
            self.critical(message)
        else:
            self.info(message)  # Default to info

    def log_performance(self, operation, duration, details=None):
        """
        Log performance metrics.
        
        Args:
            operation (str): Operation being measured
            duration (float): Duration in seconds
            details (str): Additional performance details
        """
        details_str = f" | {details}" if details else ""
        self.info(f"Performance: {operation} completed in {duration:.3f}s{details_str}")

    def log_user_action(self, action, context=None):
        """
        Log user actions for audit trail.
        
        Args:
            action (str): User action description
            context (str): Additional context about the action
        """
        context_str = f" | Context: {context}" if context else ""
        self.info(f"User Action: {action}{context_str}")

    def set_log_level(self, level):
        """
        Change the logging level.
        
        Args:
            level (str): New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            numeric_level = getattr(logging, level.upper())
            self.logger.setLevel(numeric_level)
            self.log_level = numeric_level
            self.info(f"Log level changed to: {level.upper()}")
        except AttributeError:
            self.error(f"Invalid log level: {level}")

    def get_log_stats(self):
        """
        Get logging statistics.
        
        Returns:
            dict: Logging statistics and configuration
        """
        stats = {
            'logger_name': self.name,
            'current_level': logging.getLevelName(self.log_level),
            'log_to_file': self.log_to_file,
            'handlers_count': len(self.logger.handlers),
            'log_dir': str(self.log_dir) if self.log_to_file else None,
            'log_file': str(self.log_file_path) if hasattr(self, 'log_file_path') else None
        }
        
        return stats

    def cleanup_old_logs(self, days_to_keep=30):
        """
        Clean up old log files.
        
        Args:
            days_to_keep (int): Number of days to keep log files
        """
        if not self.log_to_file or not self.log_dir.exists():
            return
        
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for log_file in self.log_dir.glob('runit_*.log'):
                try:
                    file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                    age_days = (current_time - file_modified).days
                    
                    if age_days > days_to_keep:
                        log_file.unlink()
                        deleted_count += 1
                        
                except (OSError, IOError):
                    continue  # Skip files we can't process
            
            if deleted_count > 0:
                self.info(f"Cleaned up {deleted_count} old log files (older than {days_to_keep} days)")
                
        except Exception as e:
            self.error(f"Error during log cleanup: {e}")

    def get_recent_logs(self, max_lines=100):
        """
        Get recent log entries from the current log file.
        
        Args:
            max_lines (int): Maximum number of lines to return
            
        Returns:
            list: List of recent log lines
        """
        if not hasattr(self, 'log_file_path') or not self.log_file_path.exists():
            return []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Return last max_lines lines
            return lines[-max_lines:] if len(lines) > max_lines else lines
            
        except (OSError, IOError) as e:
            self.error(f"Error reading log file: {e}")
            return []

    def close(self):
        """Close all logging handlers."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

    def __del__(self):
        """Cleanup when logger is destroyed."""
        try:
            self.close()
        except:
            pass  # Ignore cleanup errors

