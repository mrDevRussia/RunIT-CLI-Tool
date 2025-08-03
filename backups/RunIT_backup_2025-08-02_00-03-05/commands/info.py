"""
File Information Module for RunIT CLI Tool.
Provides detailed information about files including statistics and code analysis.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from utils.file_utils import FileUtils
from utils.lang_utils import LanguageUtils
from utils.logger import Logger


class FileInfo:
    """
    Provides comprehensive information about files including
    basic stats, code analysis, and metadata.
    """

    def __init__(self):
        """Initialize the FileInfo with utilities."""
        self.file_utils = FileUtils()
        self.lang_utils = LanguageUtils()
        self.logger = Logger()

    def get_basic_file_info(self, file_path):
        """
        Get basic file information.
        
        Args:
            file_path (Path): Path object of the file
            
        Returns:
            dict: Basic file information
        """
        try:
            stat = file_path.stat()
            
            return {
                'name': file_path.name,
                'full_path': str(file_path.resolve()),
                'size': stat.st_size,
                'size_formatted': self.file_utils.get_file_size(file_path),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime),
                'extension': file_path.suffix.lower(),
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'is_executable': os.access(file_path, os.X_OK)
            }
        except Exception as e:
            self.logger.error(f"Error getting basic file info: {e}")
            return None

    def analyze_text_content(self, content):
        """
        Analyze text content for statistics.
        
        Args:
            content (str): File content
            
        Returns:
            dict: Text analysis results
        """
        lines = content.split('\n')
        words = content.split()
        
        # Count different types of lines
        empty_lines = sum(1 for line in lines if not line.strip())
        comment_lines = 0
        code_lines = 0
        
        # Basic comment detection (works for many languages)
        comment_patterns = [r'^\s*#', r'^\s*//', r'^\s*/\*', r'^\s*\*', r'^\s*<!--']
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            is_comment = any(re.match(pattern, line) for pattern in comment_patterns)
            if is_comment:
                comment_lines += 1
            else:
                code_lines += 1
        
        # Character analysis
        char_counts = {
            'total': len(content),
            'letters': sum(1 for c in content if c.isalpha()),
            'digits': sum(1 for c in content if c.isdigit()),
            'spaces': sum(1 for c in content if c.isspace()),
            'punctuation': sum(1 for c in content if not c.isalnum() and not c.isspace())
        }
        
        # Word statistics
        word_lengths = [len(word) for word in words]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        
        return {
            'total_lines': len(lines),
            'empty_lines': empty_lines,
            'comment_lines': comment_lines,
            'code_lines': code_lines,
            'total_words': len(words),
            'unique_words': len(set(word.lower() for word in words)),
            'characters': char_counts,
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'average_word_length': avg_word_length,
            'longest_line': max(len(line) for line in lines) if lines else 0
        }

    def analyze_code_structure(self, content, extension):
        """
        Analyze code structure for supported languages.
        
        Args:
            content (str): File content
            extension (str): File extension
            
        Returns:
            dict: Code structure analysis
        """
        structure = {
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'constants': []
        }
        
        try:
            if extension in ['.py']:
                structure.update(self._analyze_python_code(content))
            elif extension in ['.js', '.ts']:
                structure.update(self._analyze_javascript_code(content))
            elif extension in ['.java']:
                structure.update(self._analyze_java_code(content))
            elif extension in ['.c', '.cpp']:
                structure.update(self._analyze_c_cpp_code(content))
            elif extension in ['.php']:
                structure.update(self._analyze_php_code(content))
        except Exception as e:
            self.logger.error(f"Error analyzing code structure: {e}")
        
        return structure

    def _analyze_python_code(self, content):
        """Analyze Python code structure."""
        structure = {'functions': [], 'classes': [], 'imports': []}
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Function definitions
            func_match = re.match(r'def\s+(\w+)\s*\(', stripped)
            if func_match:
                structure['functions'].append({
                    'name': func_match.group(1),
                    'line': i,
                    'type': 'function'
                })
            
            # Class definitions
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                structure['classes'].append({
                    'name': class_match.group(1),
                    'line': i,
                    'type': 'class'
                })
            
            # Import statements
            import_match = re.match(r'(?:import|from)\s+(\w+)', stripped)
            if import_match:
                structure['imports'].append({
                    'module': import_match.group(1),
                    'line': i,
                    'statement': stripped
                })
        
        return structure

    def _analyze_javascript_code(self, content):
        """Analyze JavaScript/TypeScript code structure."""
        structure = {'functions': [], 'classes': [], 'imports': []}
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Function definitions
            func_patterns = [
                r'function\s+(\w+)\s*\(',
                r'(\w+)\s*:\s*function\s*\(',
                r'const\s+(\w+)\s*=\s*\(',
                r'let\s+(\w+)\s*=\s*\(',
                r'var\s+(\w+)\s*=\s*\('
            ]
            
            for pattern in func_patterns:
                func_match = re.match(pattern, stripped)
                if func_match:
                    structure['functions'].append({
                        'name': func_match.group(1),
                        'line': i,
                        'type': 'function'
                    })
                    break
            
            # Class definitions
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                structure['classes'].append({
                    'name': class_match.group(1),
                    'line': i,
                    'type': 'class'
                })
            
            # Import statements
            import_patterns = [
                r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            ]
            
            for pattern in import_patterns:
                import_match = re.search(pattern, stripped)
                if import_match:
                    structure['imports'].append({
                        'module': import_match.group(1),
                        'line': i,
                        'statement': stripped
                    })
                    break
        
        return structure

    def _analyze_java_code(self, content):
        """Analyze Java code structure."""
        structure = {'functions': [], 'classes': [], 'imports': []}
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Method definitions
            method_match = re.search(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', stripped)
            if method_match and not re.match(r'^\s*(?:class|interface)', stripped):
                structure['functions'].append({
                    'name': method_match.group(1),
                    'line': i,
                    'type': 'method'
                })
            
            # Class definitions
            class_match = re.match(r'(?:public\s+)?class\s+(\w+)', stripped)
            if class_match:
                structure['classes'].append({
                    'name': class_match.group(1),
                    'line': i,
                    'type': 'class'
                })
            
            # Import statements
            import_match = re.match(r'import\s+([^;]+);', stripped)
            if import_match:
                structure['imports'].append({
                    'module': import_match.group(1),
                    'line': i,
                    'statement': stripped
                })
        
        return structure

    def _analyze_c_cpp_code(self, content):
        """Analyze C/C++ code structure."""
        structure = {'functions': [], 'classes': [], 'imports': []}
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Function definitions (basic detection)
            func_match = re.match(r'\w+\s+(\w+)\s*\([^)]*\)\s*{?', stripped)
            if func_match and not stripped.startswith('//') and '{' in stripped:
                structure['functions'].append({
                    'name': func_match.group(1),
                    'line': i,
                    'type': 'function'
                })
            
            # Include statements
            include_match = re.match(r'#include\s*[<"]([^>"]+)[>"]', stripped)
            if include_match:
                structure['imports'].append({
                    'module': include_match.group(1),
                    'line': i,
                    'statement': stripped
                })
        
        return structure

    def _analyze_php_code(self, content):
        """Analyze PHP code structure."""
        structure = {'functions': [], 'classes': [], 'imports': []}
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Function definitions
            func_match = re.match(r'function\s+(\w+)\s*\(', stripped)
            if func_match:
                structure['functions'].append({
                    'name': func_match.group(1),
                    'line': i,
                    'type': 'function'
                })
            
            # Class definitions
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                structure['classes'].append({
                    'name': class_match.group(1),
                    'line': i,
                    'type': 'class'
                })
            
            # Include/require statements
            include_match = re.match(r'(?:include|require)(?:_once)?\s*\(?[\'"]([^\'"]+)[\'"]', stripped)
            if include_match:
                structure['imports'].append({
                    'module': include_match.group(1),
                    'line': i,
                    'statement': stripped
                })
        
        return structure

    def format_file_info(self, file_info, text_analysis, code_structure):
        """
        Format and display comprehensive file information.
        
        Args:
            file_info (dict): Basic file information
            text_analysis (dict): Text content analysis
            code_structure (dict): Code structure analysis
        """
        print(f"\n📊 File Information: {file_info['name']}")
        print("=" * 60)
        
        # Basic Information
        print("📁 Basic Information:")
        print(f"   Full Path: {file_info['full_path']}")
        print(f"   Size: {file_info['size_formatted']} ({file_info['size']:,} bytes)")
        print(f"   Extension: {file_info['extension'] or 'None'}")
        print(f"   Created: {file_info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Permissions
        permissions = []
        if file_info['is_readable']:
            permissions.append('Read')
        if file_info['is_writable']:
            permissions.append('Write')
        if file_info['is_executable']:
            permissions.append('Execute')
        print(f"   Permissions: {', '.join(permissions) if permissions else 'None'}")
        
        print("\n📝 Content Analysis:")
        print(f"   Total Lines: {text_analysis['total_lines']:,}")
        print(f"   Code Lines: {text_analysis['code_lines']:,}")
        print(f"   Comment Lines: {text_analysis['comment_lines']:,}")
        print(f"   Empty Lines: {text_analysis['empty_lines']:,}")
        print(f"   Total Words: {text_analysis['total_words']:,}")
        print(f"   Unique Words: {text_analysis['unique_words']:,}")
        print(f"   Total Characters: {text_analysis['characters']['total']:,}")
        
        print("\n📏 Line & Word Statistics:")
        print(f"   Average Line Length: {text_analysis['average_line_length']:.1f} characters")
        print(f"   Longest Line: {text_analysis['longest_line']:,} characters")
        print(f"   Average Word Length: {text_analysis['average_word_length']:.1f} characters")
        
        print("\n🔤 Character Breakdown:")
        chars = text_analysis['characters']
        print(f"   Letters: {chars['letters']:,} ({chars['letters']/chars['total']*100:.1f}%)")
        print(f"   Digits: {chars['digits']:,} ({chars['digits']/chars['total']*100:.1f}%)")
        print(f"   Spaces: {chars['spaces']:,} ({chars['spaces']/chars['total']*100:.1f}%)")
        print(f"   Punctuation: {chars['punctuation']:,} ({chars['punctuation']/chars['total']*100:.1f}%)")
        
        # Code Structure (if applicable)
        if any(code_structure.values()):
            print("\n🏗️  Code Structure:")
            
            if code_structure['functions']:
                print(f"   Functions/Methods: {len(code_structure['functions'])}")
                for func in code_structure['functions'][:5]:  # Show first 5
                    print(f"     • {func['name']} (line {func['line']})")
                if len(code_structure['functions']) > 5:
                    print(f"     ... and {len(code_structure['functions']) - 5} more")
            
            if code_structure['classes']:
                print(f"   Classes: {len(code_structure['classes'])}")
                for cls in code_structure['classes'][:5]:  # Show first 5
                    print(f"     • {cls['name']} (line {cls['line']})")
                if len(code_structure['classes']) > 5:
                    print(f"     ... and {len(code_structure['classes']) - 5} more")
            
            if code_structure['imports']:
                print(f"   Imports/Includes: {len(code_structure['imports'])}")
                for imp in code_structure['imports'][:5]:  # Show first 5
                    print(f"     • {imp['module']} (line {imp['line']})")
                if len(code_structure['imports']) > 5:
                    print(f"     ... and {len(code_structure['imports']) - 5} more")

    def show_file_info(self, filename):
        """
        Main method to display comprehensive file information.
        
        Args:
            filename (str): Name or path of the file to analyze
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
            
            self.logger.info(f"Getting file info: {file_path}")
            
            # Get basic file information
            file_info = self.get_basic_file_info(file_path)
            if not file_info:
                print(f"❌ Unable to get file information for '{filename}'")
                return
            
            # Check file size for content analysis
            if file_info['size'] > 10 * 1024 * 1024:  # 10MB limit
                print(f"⚠️  File '{filename}' is very large ({file_info['size_formatted']})")
                response = input("Continue with content analysis? This may take a while (y/n): ").lower()
                if response not in ['y', 'yes']:
                    # Show basic info only
                    print(f"\n📊 Basic File Information: {file_info['name']}")
                    print("=" * 60)
                    print(f"   Full Path: {file_info['full_path']}")
                    print(f"   Size: {file_info['size_formatted']} ({file_info['size']:,} bytes)")
                    print(f"   Extension: {file_info['extension'] or 'None'}")
                    print(f"   Created: {file_info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                    return
            
            # Read and analyze file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encodings
                encodings = ['latin-1', 'cp1252', 'utf-16']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    print(f"❌ Unable to read file content for analysis")
                    return
            
            # Perform analyses
            text_analysis = self.analyze_text_content(content)
            code_structure = self.analyze_code_structure(content, file_info['extension'])
            
            # Format and display results
            self.format_file_info(file_info, text_analysis, code_structure)
            
            self.logger.info(f"File info completed: {file_path}")
            
        except PermissionError:
            print(f"❌ Permission denied: Cannot read file '{filename}'")
        except Exception as e:
            self.logger.error(f"Error getting file info for {filename}: {e}")
            print(f"❌ Error analyzing file: {e}")

    def compare_files(self, filename1, filename2):
        """
        Compare two files and show differences in their information.
        
        Args:
            filename1 (str): First file to compare
            filename2 (str): Second file to compare
        """
        print(f"📊 Comparing files: {filename1} vs {filename2}")
        print("=" * 60)
        
        # This could be implemented as an extension
        # For now, just show info for both files
        print("File 1:")
        self.show_file_info(filename1)
        
        print("\n" + "="*60)
        print("File 2:")
        self.show_file_info(filename2)
