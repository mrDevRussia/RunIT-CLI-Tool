"""
Language Utilities Module for RunIT CLI Tool.
Provides programming language detection, metadata, and language-specific utilities.
"""

import re
from pathlib import Path


class LanguageUtils:
    """
    Utility class for programming language detection and metadata.
    Provides methods for identifying languages, getting syntax information, and language-specific operations.
    """
    def __init__(self):
        """Initialize language utilities with language definitions."""
        self.language_definitions = self._init_language_definitions()

    def _init_language_definitions(self):
      
        """
        Initialize comprehensive language definitions with metadata.
        
        Returns:
            dict: Language definitions with extensions, metadata, and patterns
        """
        return {
            'python': {
                'extensions': ['.py', '.pyw', '.pyx', '.pyz'],
                'primary_extension': '.py',
                'interpreter': 'python',
                'compiler': None,
                'category': 'interpreted',
                'description': 'Python Programming Language',
                'comment_styles': {
                    'single_line': '#',
                    'multi_line': None,
                    'docstring': '"""'
                },
                'keywords': [
                    'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while',
                    'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'lambda',
                    'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'
                ],
                'function_patterns': [
                    r'def\s+(\w+)\s*\(',
                    r'async\s+def\s+(\w+)\s*\('
                ],
                'class_patterns': [r'class\s+(\w+)'],
                'import_patterns': [
                    r'import\s+(\w+)',
                    r'from\s+(\w+)\s+import'
                ]
            },
            
            'javascript': {
                'extensions': ['.js', '.jsx', '.mjs'],
                'primary_extension': '.js',
                'interpreter': 'node',
                'compiler': None,
                'category': 'interpreted',
                'description': 'JavaScript Programming Language',
                'comment_styles': {
                    'single_line': '//',
                    'multi_line': ('/*', '*/'),
                    'docstring': None
                },
                'keywords': [
                    'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'do',
                    'switch', 'case', 'default', 'break', 'continue', 'return', 'try',
                    'catch', 'finally', 'throw', 'new', 'this', 'typeof', 'instanceof'
                ],
                'function_patterns': [
                    r'function\s+(\w+)\s*\(',
                    r'(\w+)\s*:\s*function\s*\(',
                    r'const\s+(\w+)\s*=\s*\(',
                    r'let\s+(\w+)\s*=\s*\(',
                    r'var\s+(\w+)\s*=\s*\('
                ],
                'class_patterns': [r'class\s+(\w+)'],
                'import_patterns': [
                    r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',
                    r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
                ]
            },
            
            'typescript': {
                'extensions': ['.ts', '.tsx'],
                'primary_extension': '.ts',
                'interpreter': 'ts-node',
                'compiler': 'tsc',
                'category': 'compiled',
                'description': 'TypeScript Programming Language',
                'comment_styles': {
                    'single_line': '//',
                    'multi_line': ('/*', '*/'),
                    'docstring': None
                },
                'keywords': [
                    'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'do',
                    'switch', 'case', 'default', 'break', 'continue', 'return', 'try',
                    'catch', 'finally', 'throw', 'new', 'this', 'typeof', 'instanceof',
                    'interface', 'type', 'enum', 'namespace', 'declare', 'abstract'
                ],
                'function_patterns': [
                    r'function\s+(\w+)\s*\(',
                    r'(\w+)\s*\([^)]*\)\s*:\s*\w+\s*=>',
                    r'const\s+(\w+)\s*=\s*\(',
                    r'let\s+(\w+)\s*=\s*\('
                ],
                'class_patterns': [r'class\s+(\w+)', r'interface\s+(\w+)'],
                'import_patterns': [
                    r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',
                    r'import\s+[\'"]([^\'"]+)[\'"]'
                ]
            },
            
            'java': {
                'extensions': ['.java'],
                'primary_extension': '.java',
                'interpreter': None,
                'compiler': 'javac',
                'category': 'compiled',
                'description': 'Java Programming Language',
                'comment_styles': {
                    'single_line': '//',
                    'multi_line': ('/*', '*/'),
                    'docstring': ('/**', '*/')
                },
                'keywords': [
                    'public', 'private', 'protected', 'static', 'final', 'class', 'interface',
                    'extends', 'implements', 'abstract', 'void', 'int', 'double', 'boolean',
                    'String', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
                    'continue', 'return', 'try', 'catch', 'finally', 'throw', 'throws'
                ],
                'function_patterns': [
                    r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\('
                ],
                'class_patterns': [
                    r'(?:public\s+)?class\s+(\w+)',
                    r'(?:public\s+)?interface\s+(\w+)'
                ],
                'import_patterns': [r'import\s+([^;]+);']
            },
            
            'c': {
                'extensions': ['.c', '.h'],
                'primary_extension': '.c',
                'interpreter': None,
                'compiler': 'gcc',
                'category': 'compiled',
                'description': 'C Programming Language',
                'comment_styles': {
                    'single_line': '//',
                    'multi_line': ('/*', '*/'),
                    'docstring': None
                },
                'keywords': [
                    'int', 'char', 'float', 'double', 'void', 'if', 'else', 'for', 'while',
                    'do', 'switch', 'case', 'break', 'continue', 'return', 'struct', 'union',
                    'enum', 'typedef', 'static', 'extern', 'const', 'volatile', 'sizeof'
                ],
                'function_patterns': [r'\w+\s+(\w+)\s*\([^)]*\)\s*{'],
                'class_patterns': [r'struct\s+(\w+)', r'typedef\s+struct\s+(\w+)'],
                'import_patterns': [r'#include\s*[<"]([^>"]+)[>"]']
            },
            
            'cpp': {
                'extensions': ['.cpp', '.cxx', '.cc', '.C', '.hpp', '.hxx', '.hh'],
                'primary_extension': '.cpp',
                'interpreter': None,
                'compiler': 'g++',
                'category': 'compiled',
                'description': 'C++ Programming Language',
                'comment_styles': {
                    'single_line': '//',
                    'multi_line': ('/*', '*/'),
                    'docstring': None
                },
                'keywords': [
                    'int', 'char', 'float', 'double', 'void', 'bool', 'if', 'else', 'for',
                    'while', 'do', 'switch', 'case', 'break', 'continue', 'return', 'class',
                    'struct', 'union', 'enum', 'namespace', 'using', 'template', 'typename',
                    'public', 'private', 'protected', 'virtual', 'static', 'const', 'inline'
                ],
                'function_patterns': [
                    r'\w+\s+(\w+)\s*\([^)]*\)\s*{',
                    r'(\w+)::\w+\s*\([^)]*\)\s*{'
                ],
                'class_patterns': [
                    r'class\s+(\w+)',
                    r'struct\s+(\w+)',
                    r'namespace\s+(\w+)'
                ],
                'import_patterns': [
                    r'#include\s*[<"]([^>"]+)[>"]',
                    r'using\s+namespace\s+(\w+);'
                ]
            },
            
            'php': {
                'extensions': ['.php', '.phtml', '.php3', '.php4', '.php5', '.phps'],
                'primary_extension': '.php',
                'interpreter': 'php',
                'compiler': None,
                'category': 'interpreted',
                'description': 'PHP Programming Language',
                'comment_styles': {
                    'single_line': '//',
                    'multi_line': ('/*', '*/'),
                    'docstring': ('/**', '*/')
                },
                'keywords': [
                    'function', 'class', 'interface', 'trait', 'namespace', 'use', 'public',
                    'private', 'protected', 'static', 'final', 'abstract', 'if', 'else',
                    'elseif', 'for', 'foreach', 'while', 'do', 'switch', 'case', 'break',
                    'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new'
                ],
                'function_patterns': [r'function\s+(\w+)\s*\('],
                'class_patterns': [
                    r'class\s+(\w+)',
                    r'interface\s+(\w+)',
                    r'trait\s+(\w+)'
                ],
                'import_patterns': [
                    r'(?:include|require)(?:_once)?\s*\(?[\'"]([^\'"]+)[\'"]',
                    r'use\s+([^;]+);'
                ]
            },
            
            'html': {
                'extensions': ['.html', '.htm', '.xhtml'],
                'primary_extension': '.html',
                'interpreter': 'browser',
                'compiler': None,
                'category': 'markup',
                'description': 'HyperText Markup Language',
                'comment_styles': {
                    'single_line': None,
                    'multi_line': ('<!--', '-->'),
                    'docstring': None
                },
                'keywords': [
                    'html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style',
                    'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img',
                    'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button'
                ],
                'function_patterns': [],
                'class_patterns': [],
                'import_patterns': [
                    r'<link[^>]*href=[\'"]([^\'"]+)[\'"]',
                    r'<script[^>]*src=[\'"]([^\'"]+)[\'"]'
                ]
            },
            
            'css': {
                'extensions': ['.css', '.scss', '.sass', '.less'],
                'primary_extension': '.css',
                'interpreter': 'browser',
                'compiler': None,
                'category': 'stylesheet',
                'description': 'Cascading Style Sheets',
                'comment_styles': {
                    'single_line': None,
                    'multi_line': ('/*', '*/'),
                    'docstring': None
                },
                'keywords': [
                    'color', 'background', 'font', 'margin', 'padding', 'border', 'width',
                    'height', 'position', 'display', 'float', 'clear', 'z-index', 'opacity'
                ],
                'function_patterns': [],
                'class_patterns': [r'\.(\w+)\s*{'],
                'import_patterns': [r'@import\s+[\'"]([^\'"]+)[\'"]']
            },
            
            'batch': {
                'extensions': ['.bat', '.cmd'],
                'primary_extension': '.bat',
                'interpreter': 'cmd',
                'compiler': None,
                'category': 'script',
                'description': 'Windows Batch Script',
                'comment_styles': {
                    'single_line': 'REM',
                    'multi_line': None,
                    'docstring': None
                },
                'keywords': [
                    'echo', 'set', 'if', 'else', 'for', 'goto', 'call', 'pause', 'exit',
                    'cd', 'dir', 'copy', 'move', 'del', 'md', 'rd', 'type', 'cls'
                ],
                'function_patterns': [r':(\w+)'],
                'class_patterns': [],
                'import_patterns': [r'call\s+([^\s]+)']
            },
            
            'shell': {
                'extensions': ['.sh', '.bash', '.zsh', '.fish'],
                'primary_extension': '.sh',
                'interpreter': 'bash',
                'compiler': None,
                'category': 'script',
                'description': 'Shell Script',
                'comment_styles': {
                    'single_line': '#',
                    'multi_line': None,
                    'docstring': None
                },
                'keywords': [
                    'if', 'then', 'else', 'elif', 'fi', 'for', 'while', 'do', 'done',
                    'case', 'esac', 'function', 'return', 'exit', 'echo', 'printf',
                    'read', 'test', 'true', 'false'
                ],
                'function_patterns': [
                    r'function\s+(\w+)\s*\(',
                    r'(\w+)\s*\(\)\s*{'
                ],
                'class_patterns': [],
                'import_patterns': [
                    r'source\s+([^\s]+)',
                    r'\.\s+([^\s]+)'
                ]
            }
        }

    def detect_language_by_extension(self, file_path):
        """
        Detect programming language by file extension.
        
        Args:
            file_path (str or Path): Path to the file
            
        Returns:
            str: Detected language name, or None if not found
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        extension = file_path.suffix.lower()
        
        for lang_name, lang_info in self.language_definitions.items():
            if extension in lang_info['extensions']:
                return lang_name
        
        return None

    def detect_language_by_content(self, content, max_lines=50):
        """
        Detect programming language by analyzing file content.
        
        Args:
            content (str): File content to analyze
            max_lines (int): Maximum lines to analyze
            
        Returns:
            tuple: (language_name, confidence_score)
        """
        lines = content.split('\n')[:max_lines]
        content_sample = '\n'.join(lines)
        
        language_scores = {}
        
        for lang_name, lang_info in self.language_definitions.items():
            score = 0
            
            # Check for keywords
            keywords = lang_info.get('keywords', [])
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, content_sample, re.IGNORECASE))
                score += matches
            
            # Check for function patterns
            function_patterns = lang_info.get('function_patterns', [])
            for pattern in function_patterns:
                matches = len(re.findall(pattern, content_sample, re.MULTILINE))
                score += matches * 3  # Functions are strong indicators
            
            # Check for class patterns
            class_patterns = lang_info.get('class_patterns', [])
            for pattern in class_patterns:
                matches = len(re.findall(pattern, content_sample, re.MULTILINE))
                score += matches * 2  # Classes are good indicators
            
            # Check for import patterns
            import_patterns = lang_info.get('import_patterns', [])
            for pattern in import_patterns:
                matches = len(re.findall(pattern, content_sample, re.MULTILINE))
                score += matches * 2  # Imports are good indicators
            
            # Special checks for specific languages
            if lang_name == 'python':
                # Check for Python-specific patterns
                if re.search(r'def\s+\w+\s*\([^)]*\)\s*:', content_sample):
                    score += 5
                if re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]', content_sample):
                    score += 5
            
            elif lang_name == 'php':
                # Check for PHP tags
                if re.search(r'<\?php', content_sample):
                    score += 10
                if re.search(r'\$\w+', content_sample):  # Variables
                    score += 3
            
            elif lang_name == 'html':
                # Check for HTML tags
                if re.search(r'<!DOCTYPE\s+html>', content_sample, re.IGNORECASE):
                    score += 10
                if re.search(r'</?html[^>]*>', content_sample, re.IGNORECASE):
                    score += 5
            
            elif lang_name == 'css':
                # Check for CSS selectors and properties
                if re.search(r'\w+\s*:\s*[^;]+;', content_sample):
                    score += 3
                if re.search(r'[.#]\w+\s*{', content_sample):
                    score += 5
            
            if score > 0:
                language_scores[lang_name] = score
        
        if not language_scores:
            return None, 0
        
        # Find language with highest score
        best_language = max(language_scores, key=language_scores.get)
        max_score = language_scores[best_language]
        
        # Calculate confidence (normalize score)
        total_possible = sum(language_scores.values())
        confidence = max_score / total_possible if total_possible > 0 else 0
        
        return best_language, confidence

    def get_language_info(self, language_name):
        """
        Get detailed information about a programming language.
        
        Args:
            language_name (str): Name of the language
            
        Returns:
            dict: Language information, or None if not found
        """
        return self.language_definitions.get(language_name.lower())

    def get_supported_languages(self):
        """
        Get list of all supported programming languages.
        
        Returns:
            list: List of supported language names
        """
        return list(self.language_definitions.keys())

    def get_languages_by_category(self, category):
        """
        Get languages filtered by category.
        
        Args:
            category (str): Category to filter by
            
        Returns:
            list: List of language names in the category
        """
        return [
            lang_name for lang_name, lang_info in self.language_definitions.items()
            if lang_info.get('category') == category
        ]

    def is_compiled_language(self, language_name):
        """
        Check if a language is compiled.
        
        Args:
            language_name (str): Language name
            
        Returns:
            bool: True if compiled, False if interpreted
        """
        lang_info = self.get_language_info(language_name)
        if lang_info:
            return lang_info.get('category') == 'compiled'
        return False

    def get_required_tools(self, language_name):
        """
        Get required tools (interpreter/compiler) for a language.
        
        Args:
            language_name (str): Language name
            
        Returns:
            dict: Required tools information
        """
        lang_info = self.get_language_info(language_name)
        if not lang_info:
            return None
        
        tools = {
            'interpreter': lang_info.get('interpreter'),
            'compiler': lang_info.get('compiler'),
            'category': lang_info.get('category'),
            'primary_tool': lang_info.get('compiler') or lang_info.get('interpreter')
        }
        
        return tools

    def get_file_template(self, language_name, filename):
        """
        Get a basic file template for a language.
        
        Args:
            language_name (str): Language name
            filename (str): Name of the file being created
            
        Returns:
            str: Basic template content, or None if not available
        """
        lang_info = self.get_language_info(language_name)
        if not lang_info:
            return None
        
        # This could be expanded to return more sophisticated templates
        comment_char = lang_info.get('comment_styles', {}).get('single_line', '#')
        
        basic_template = f"{comment_char} {filename}\n{comment_char} Created with RunIT\n\n"
        
        # Add language-specific starter code
        if language_name == 'python':
            basic_template += 'def main():\n    """Main function."""\n    pass\n\nif __name__ == "__main__":\n    main()\n'
        elif language_name in ['javascript', 'typescript']:
            basic_template += 'function main() {\n    // Your code here\n}\n\nmain();\n'
        elif language_name == 'java':
            class_name = Path(filename).stem
            basic_template += f'public class {class_name} {{\n    public static void main(String[] args) {{\n        // Your code here\n    }}\n}}\n'
        elif language_name in ['c', 'cpp']:
            basic_template += '#include <stdio.h>\n\nint main() {\n    // Your code here\n    return 0;\n}\n'
        
        return basic_template

    def analyze_code_complexity(self, content, language_name):
        """
        Analyze basic code complexity metrics.
        
        Args:
            content (str): Code content
            language_name (str): Programming language
            
        Returns:
            dict: Complexity metrics
        """
        lang_info = self.get_language_info(language_name)
        if not lang_info:
            return None
        
        lines = content.split('\n')
        
        # Count different types of constructs
        function_count = 0
        class_count = 0
        import_count = 0
        comment_lines = 0
        code_lines = 0
        
        # Get patterns for this language
        function_patterns = lang_info.get('function_patterns', [])
        class_patterns = lang_info.get('class_patterns', [])
        import_patterns = lang_info.get('import_patterns', [])
        
        comment_style = lang_info.get('comment_styles', {})
        single_comment = comment_style.get('single_line')
        multi_comment = comment_style.get('multi_line')
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for comments
            is_comment = False
            if single_comment and stripped.startswith(single_comment):
                is_comment = True
            elif multi_comment and (multi_comment[0] in stripped or multi_comment[1] in stripped):
                is_comment = True
            
            if is_comment:
                comment_lines += 1
            else:
                code_lines += 1
            
            # Count functions
            for pattern in function_patterns:
                if re.search(pattern, line):
                    function_count += 1
                    break
            
            # Count classes
            for pattern in class_patterns:
                if re.search(pattern, line):
                    class_count += 1
                    break
            
            # Count imports
            for pattern in import_patterns:
                if re.search(pattern, line):
                    import_count += 1
                    break
        
        return {
            'total_lines': len(lines),
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'function_count': function_count,
            'class_count': class_count,
            'import_count': import_count,
            'complexity_score': function_count + class_count * 2,  # Simple metric
            'comment_ratio': comment_lines / len(lines) if lines else 0
        }

