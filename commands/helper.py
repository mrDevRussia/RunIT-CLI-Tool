"""
Help Display Module for RunIT CLI Tool.
Provides comprehensive help information and usage examples.
"""

from utils.logger import Logger


class HelpDisplay:
    """
    Handles displaying help information, usage examples,
    and command documentation for the RunIT CLI tool.
    """

    def __init__(self):
        """Initialize the HelpDisplay."""
        self.logger = Logger()

    def show_general_help(self):
        """Display general help information with all available commands."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                      RunIT v1.1.0 - Help                     ║
║              Smart Terminal Assistant for Windows            ║
║                Always for you, alwways with you              ║
╚══════════════════════════════════════════════════════════════╝

📋 AVAILABLE COMMANDS:

🔧 FILE EXECUTION:
   run <filename>                 Run files with auto-detection
   
   Examples:
   • run script.py              → Execute Python script
   • run app.js                 → Execute JavaScript with Node.js
   • run page.html              → Open HTML in default browser
   • run program.bat            → Execute batch file
   • run code.c                 → Compile and run C program

📝 FILE CREATION:
   create <language> <filename>   Create new files with boilerplate
   
   Examples:
   • create python hello.py      → Create Python script
   • create javascript app.js    → Create JavaScript file  
   • create html index.html      → Create HTML page
   • create batch script.bat     → Create batch file

🔍 FILE SEARCH:
   search <keyword> <filename>    Search for keywords in files
   
   Examples:
   • search "function" script.py → Find all functions
   • search "TODO" *.txt         → Find TODO comments
   • search "error" log.txt      → Find error messages

🛡️  FILE SCANNING:
   scan <filename>                Scan files for suspicious patterns
   
   Examples:
   • scan script.py              → Check for malicious code
   • scan download.exe           → Virus pattern detection
   • scan suspicious.js          → Analyze JavaScript safety

📊 FILE INFORMATION:
   info <filename>                Get detailed file information
   
   Examples:
   • info document.txt           → Show file stats
   • info source.py              → Analyze code structure
   • info data.json              → Content analysis

📦 PACKAGE SYSTEM (NEW v1.1):
   install <package@latest>       Install packages
   update <package@latest>        Update packages or tool
   version                        Show version and package status
   
   Examples:
   • install preview_RunIT@latest → Install HTML preview package
   • install Edit_RunIT@latest    → Install advanced editor package
   • update RunIT@latest          → Update the main tool

📁 FILE MANAGEMENT (NEW v1.1):
   show <file_or_directory>       Show file/directory structure
   edit <filename> [editor]       Edit files with available editors
   go <directory_path>            Navigate to directory
   
   Examples:
   • show project/                → Display directory tree
   • show main.py                 → Show file details and structure
   • edit config.txt              → Edit file with default editor
   • go C:\\Users\\Projects       → Change to directory

🎯 PACKAGE COMMANDS (When Installed):
   preview <filename.html>        Preview HTML files in browser
   
🔧 UTILITY COMMANDS:
   help [command]                Show help (general or specific)
   test                          Test RunIT functionality
   runai                         Use offline AI assistant
   clear                         Clear the terminal screen
   exit / quit                   Exit RunIT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SUPPORTED FILE TYPES:

Programming Languages:
• Python (.py)        • JavaScript (.js)     • TypeScript (.ts)
• C (.c)              • C++ (.cpp)           • Java (.java)
• PHP (.php)          • Batch (.bat, .cmd)   • Shell (.sh)

Web Technologies:
• HTML (.html)        • CSS (.css)           • JSON (.json)
• XML (.xml)

Other:
• Text files (.txt)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS:
• Use 'help <command>' for detailed command information
• File paths can be relative or absolute
• RunIT auto-detects file types by extension
• Large files will prompt before processing
• Type 'clear' to clean up your screen

🌟 For more information, visit the documentation or type:
   help <specific_command>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(help_text)

    def show_command_help(self, command):
        """
        Show detailed help for a specific command.
        
        Args:
            command (str): Command name to show help for
        """
        command_help = {
            'run': """
🚀 RUN COMMAND - Execute Files

SYNTAX:
   run <filename>

DESCRIPTION:
   Execute files with automatic interpreter detection based on file extension.
   RunIT will choose the appropriate interpreter and run your file.

SUPPORTED FILE TYPES:
   • .py    → python <file>
   • .js    → node <file>  
   • .html  → Open in default browser
   • .css   → Open with default program
   • .php   → php <file>
   • .bat   → Direct execution
   • .cmd   → Direct execution
   • .sh    → bash <file> (if available)
   • .c     → Compile with gcc, then execute
   • .cpp   → Compile with g++, then execute
   • .java  → Compile with javac, then run with java
   • .ts    → ts-node <file> (if available)
   • .json  → Open with default program
   • .xml   → Open with default program
   • .txt   → Open with default program

EXAMPLES:
   run hello.py                   Execute Python script
   run server.js                  Run JavaScript with Node.js
   run index.html                 Open HTML in browser
   run compile_me.c               Compile and run C program
   run batch_job.bat              Execute batch script

NOTES:
   • Required interpreters must be installed (python, node, etc.)
   • Compilation languages (C, C++, Java) will prompt for compile+run
   • Files opened with 'start' use Windows default program association
   • RunIT checks interpreter availability before execution
""",

            'create': """
📝 CREATE COMMAND - Generate New Files

SYNTAX:
   create <language> <filename>

DESCRIPTION:
   Create new files with language-specific boilerplate code and templates.
   Automatically adds appropriate file extensions if not provided.

SUPPORTED LANGUAGES:
   • python      → .py files with main() function template
   • javascript  → .js files with basic structure
   • html        → .html files with complete HTML5 template
   • css         → .css files with reset and base styles
   • php         → .php files with proper PHP tags
   • batch       → .bat files with basic batch structure
   • bash        → .sh files with shebang and structure
   • c           → .c files with #include and main()
   • cpp         → .cpp files with C++ includes and structure
   • java        → .java files with public class template
   • typescript  → .ts files with TypeScript structure
   • json        → .json files with basic JSON structure
   • xml         → .xml files with XML declaration
   • text        → .txt files with basic text template

EXAMPLES:
   create python calculator.py      Create Python script
   create html website.html         Create HTML page
   create javascript app.js         Create JavaScript file
   create batch install.bat         Create batch script
   create c program.c               Create C source file

FEATURES:
   • Auto-generates appropriate file extensions
   • Includes creation timestamp and author info
   • Provides language-specific boilerplate code
   • Validates filename for Windows compatibility
   • Prompts before overwriting existing files
   • Shows preview of created content
""",

            'search': """
🔍 SEARCH COMMAND - Find Keywords in Files

SYNTAX:
   search <keyword> <filename>

DESCRIPTION:
   Search for keywords within files and display results with line numbers,
   context, and highlighted matches.

FEATURES:
   • Case-insensitive search by default
   • Shows line numbers for all matches
   • Highlights matched text with ► markers
   • Displays character positions of matches
   • Groups multiple matches per line
   • Handles various text encodings

EXAMPLES:
   search "function" script.py       Find all function definitions
   search "TODO" project.txt         Find TODO comments
   search "error" log.txt            Find error messages
   search "import" main.py           Find import statements
   search "class" *.java             Find class definitions

SEARCH RESULTS INCLUDE:
   • Total number of matches found
   • Line numbers where matches occur
   • Full line content with highlighting
   • Character positions of matches
   • Multiple matches per line handling

SUPPORTED ENCODINGS:
   • UTF-8 (primary)
   • Latin-1 (fallback)
   • CP1252 (Windows)
   • UTF-16 (fallback)

NOTES:
   • Large files (>50MB) will prompt before searching
   • Empty or whitespace-only keywords are rejected
   • Search handles binary files gracefully
   • Results are grouped by line number
""",

            'scan': """
🛡️  SCAN COMMAND - Virus and Malware Detection

SYNTAX:
   scan <filename>

DESCRIPTION:
   Perform local pattern-based scanning to detect suspicious code patterns
   that might indicate malware, viruses, or malicious scripts.

DETECTION CATEGORIES:
   🔴 HIGH RISK:
   • Dynamic code execution (eval, exec, __import__)
   • Suspicious keywords (keylogger, malware, trojan)
   • Obfuscated base64 content with dangerous code

   🟠 MEDIUM RISK:  
   • Code obfuscation techniques
   • System command execution
   • Shell access patterns

   🟡 LOW RISK:
   • Network communication
   • File system operations
   • Cryptographic operations

SCAN FEATURES:
   • Pattern-based detection using regular expressions
   • Base64 decode and content analysis
   • Risk scoring and categorization
   • Detailed findings with line numbers
   • Context showing suspicious code segments

EXAMPLES:
   scan suspicious_script.py         Check Python file
   scan downloaded_file.exe          Scan executable
   scan email_attachment.js          Check JavaScript
   scan unknown_batch.bat            Analyze batch file

SCAN RESULTS INCLUDE:
   • Overall risk level (CLEAN/LOW/MEDIUM/HIGH)
   • Risk score calculation
   • Categorized findings by threat level
   • Line numbers and code context
   • Pattern matches and descriptions

LIMITATIONS:
   ⚠️  This is a basic pattern scanner, NOT a replacement for:
   • Professional antivirus software
   • Comprehensive malware analysis
   • Real-time protection systems
   
   Always use full antivirus solutions for complete protection!
""",

            'info': """
📊 INFO COMMAND - File Analysis and Statistics

SYNTAX:
   info <filename>

DESCRIPTION:
   Display comprehensive information about files including basic properties,
   content analysis, and code structure examination.

INFORMATION PROVIDED:

📁 Basic File Properties:
   • Full file path and name
   • File size (formatted and bytes)
   • Creation, modification, and access timestamps
   • File extension and type
   • File permissions (read/write/execute)

📝 Content Analysis:
   • Total lines, words, and characters
   • Code lines vs comment lines vs empty lines
   • Unique word count and vocabulary
   • Average line and word lengths
   • Character breakdown (letters, digits, spaces, punctuation)

🏗️  Code Structure (Language-Specific):
   • Functions and methods with line numbers
   • Class definitions and locations
   • Import/include statements
   • Variable and constant declarations

SUPPORTED LANGUAGES FOR CODE ANALYSIS:
   • Python (.py)     - Functions, classes, imports
   • JavaScript (.js) - Functions, classes, imports/requires
   • TypeScript (.ts) - Functions, classes, imports  
   • Java (.java)     - Methods, classes, imports
   • C/C++ (.c/.cpp)  - Functions, includes
   • PHP (.php)       - Functions, classes, includes

EXAMPLES:
   info document.txt             Basic text file analysis
   info source_code.py           Python code structure
   info application.js           JavaScript analysis
   info database.sql             SQL file statistics
   info stylesheet.css           CSS file information

FEATURES:
   • Handles multiple text encodings
   • Large file processing with user confirmation
   • Percentage breakdowns for character analysis
   • Preview of first few functions/classes/imports
   • Comprehensive statistics display

NOTES:
   • Files larger than 10MB will prompt before analysis
   • Binary files are handled gracefully
   • Code structure detection is language-specific
   • Results include both absolute numbers and percentages
""",

            'help': """
🔧 HELP COMMAND - Get Assistance

SYNTAX:
   help [command]

DESCRIPTION:
   Display help information for RunIT commands and usage.

USAGE:
   help                    Show general help with all commands
   help <command>          Show detailed help for specific command

EXAMPLES:
   help                    Show main help screen
   help run                Show detailed help for run command
   help create             Show detailed help for create command
   help search             Show detailed help for search command

AVAILABLE HELP TOPICS:
   • run      - File execution help
   • create   - File creation help  
   • search   - Keyword search help
   • scan     - Virus scanning help
   • info     - File information help
   • clear    - Terminal clearing help
   • exit     - How to quit RunIT
""",

            'clear': """
🔧 CLEAR COMMAND - Clean Terminal

SYNTAX:
   clear

DESCRIPTION:
   Clear the terminal screen and redisplay the RunIT banner.
   Equivalent to the Windows 'cls' command.

USAGE:
   Simply type 'clear' and press Enter to clean up your terminal.

EXAMPLE:
   clear                   Clear screen and show banner

NOTES:
   • Uses Windows CMD 'cls' command internally
   • Redisplays the RunIT welcome banner
   • Useful for cleaning up after long outputs
""",

            'exit': """
👋 EXIT COMMAND - Quit RunIT

SYNTAX:
   exit
   quit

DESCRIPTION:
   Exit the RunIT CLI tool and return to Windows CMD.

USAGE:
   Type 'exit' or 'quit' to leave RunIT.

EXAMPLES:
   exit                    Quit RunIT
   quit                    Same as exit

KEYBOARD SHORTCUTS:
   • Ctrl+C               Interrupt and exit
   • Ctrl+D               EOF signal (exit)

NOTES:
   • All unsaved work should be saved before exiting
   • RunIT will display a goodbye message
   • Returns control to Windows Command Prompt
"""
        }

        if command in command_help:
            print(command_help[command])
        else:
            print(f"❌ No detailed help available for command: '{command}'")
            print("Available commands: run, create, search, scan, info, help, clear, exit")
            print("Type 'help' for general help.")

    def show_startup_tips(self):
        """Display helpful tips for new users."""
        tips = """
💡 QUICK START TIPS:

1. 🚀 Run any script:        run my_script.py  
2. 📝 Create new files:      create python hello.py
3. 🔍 Search in files:       search "TODO" readme.txt
4. 🛡️  Scan for viruses:     scan suspicious_file.js
5. 📊 Get file info:         info document.txt
6. 🔧 Get help anytime:      help [command]

Type 'help' for the full command list!
"""
        print(tips)

    def show_version_info(self):
        """Display version and system information."""
        version_info = """
🚀 RunIT - Smart Terminal Assistant
Version: 1.0.0 (Phase 1)
Platform: Windows
Python: Built-in standard libraries only

📋 Current Phase Features:
✅ File execution with auto-detection
✅ Script creation with boilerplate code
✅ Keyword search with context
✅ Local virus pattern scanning
✅ Comprehensive file analysis
✅ Interactive help system

🔜 Coming in Phase 2:
• AI-powered code suggestions
• Advanced debugging tools  
• Online virus API integration
• Custom themes and configurations
• Extended language support

📬 Support: Check the documentation for troubleshooting
🌟 Open Source: Contributions welcome!
"""
        print(version_info)

    def show_keyboard_shortcuts(self):
        """Display available keyboard shortcuts."""
        shortcuts = """
⌨️  KEYBOARD SHORTCUTS:

During RunIT Session:
• Ctrl+C                   Interrupt current operation
• Ctrl+D                   Exit RunIT (EOF signal)
• Up/Down Arrow           Command history (if supported by terminal)
• Tab                     Auto-completion (if supported)

During File Execution:
• Ctrl+C                   Stop running script
• Ctrl+Z                   Suspend process (Windows)

Terminal Navigation:
• clear                    Clear screen
• exit or quit            Exit RunIT

📝 Note: Some shortcuts depend on your Windows terminal configuration.
"""
        print(shortcuts)

    def show_troubleshooting(self):
        """Display common troubleshooting information."""
        troubleshooting = """
🔧 TROUBLESHOOTING GUIDE:

Common Issues:

❌ "Interpreter not found":
   → Install required interpreter (Python, Node.js, etc.)
   → Add interpreter to Windows PATH
   → Restart CMD after installation

❌ "Permission denied":  
   → Run CMD as Administrator
   → Check file permissions
   → Ensure file is not locked by another program

❌ "File not found":
   → Check file path spelling
   → Use quotes for paths with spaces: "my file.py"
   → Verify file exists with 'dir' command

❌ "Compilation failed":
   → Install required compiler (gcc, g++, javac)
   → Check code syntax errors
   → Ensure compiler is in PATH

❌ "Encoding errors":
   → Try saving file as UTF-8
   → Check file isn't corrupted
   → Use text editor to fix encoding

🆘 If problems persist:
   1. Check the docs/README.md file
   2. Verify your Windows version compatibility
   3. Ensure all required tools are installed
   4. Try running individual commands directly in CMD
"""
        print(troubleshooting)
