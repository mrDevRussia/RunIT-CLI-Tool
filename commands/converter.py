import os
import re
from utils.logger import Logger

class Converter:
    def __init__(self):
        self.logger = Logger(__name__)
        self.language_patterns = {
            'js_to_python': {
                'function': (r'function\s+([\w_]+)\s*\(([^)]*)\)\s*{([^}]*)}', r'def \1(\2):\3'),
                'function_params': (r'\b(const|let|var)\s+([\w_]+)\s*=\s*([^,;]+)', r'\2 = \3'),
                'return_statement': (r'return\s+([^;]+);?', r'return \1'),
                'var_let_const': (r'(var|let|const)\s+([\w_]+)\s*=\s*([^;]+);', r'\2 = \3'),
                'console_log': (r'console\.log\(([^;]+)\);', r'print(\1)'),
                'array_methods': {
                    'push': (r'\.push\(([^)]+)\)', r'.append(\1)'),
                    'pop': (r'\.pop\(\)', r'.pop()'),
                    'shift': (r'\.shift\(\)', r'.pop(0)'),
                    'unshift': (r'\.unshift\(([^)]+)\)', r'.insert(0, \1)'),
                    'length': (r'\.length', r'.__len__()'),
                    'map': (r'\.map\(([^)]+)\)', r'list(map(\1, ))'),
                    'filter': (r'\.filter\(([^)]+)\)', r'list(filter(\1, ))'),
                    'forEach': (r'\.forEach\(([^)]+)\)', r'for item in '),
                    'includes': (r'\.includes\(([^)]+)\)', r'.__contains__(\1)'),
                    'indexOf': (r'\.indexOf\(([^)]+)\)', r'.index(\1)'),
                    'join': (r'\.join\(([^)]+)\)', r'.join(\1)'),
                },
                'operators': {
                    '===': '==',
                    '!==': '!=',
                    '&&': 'and',
                    '||': 'or',
                    '!': 'not ',
                    '++': ' += 1',
                    '--': ' -= 1',
                },
                'string_methods': {
                    'toLowerCase': 'lower',
                    'toUpperCase': 'upper',
                    'trim': 'strip',
                    'substring': 'slice',
                    'charAt': '__getitem__',
                    'indexOf': 'find',
                },
                'semicolon': (r';\n', r'\n'),
                'this': (r'this\.', r'self.'),
                'arrow_function': (r'\(([^)]*)\)\s*=>\s*{([^}]*)}', r'lambda \1: \2'),
                'template_literal': (r'`([^`]*)`', r'f"\1"'),
                'undefined_null': {'undefined': 'None', 'null': 'None'}
            },
            'python_to_js': {
                'function': (r'def\s+([\w_]+)\s*\(([^)]*)\):\s*([^\n]*)', r'function \1(\2) {\3}'),
                'print': (r'print\(([^)]*)\)', r'console.log(\1);'),
                'list_methods': {
                    'append': (r'\.append\(([^)]+)\)', r'.push(\1)'),
                    'pop': (r'\.pop\(\)', r'.pop()'),
                    'insert': (r'\.insert\(0,\s*([^)]+)\)', r'.unshift(\1)'),
                },
                'operators': {
                    ' and ': ' && ',
                    ' or ': ' || ',
                    'not ': '!',
                },
                'None': 'null',
            },
            'html_to_md': {
                'headings': [
                    (r'<h1[^>]*>([^<]*)</h1>', r'# \1'),
                    (r'<h2[^>]*>([^<]*)</h2>', r'## \1'),
                    (r'<h3[^>]*>([^<]*)</h3>', r'### \1'),
                ],
                'emphasis': [
                    (r'<strong[^>]*>([^<]*)</strong>', r'**\1**'),
                    (r'<em[^>]*>([^<]*)</em>', r'*\1*'),
                ],
                'links': (r'<a[^>]*href="([^"]+)"[^>]*>([^<]*)</a>', r'[\2](\1)'),
                'lists': [
                    (r'<ul[^>]*>([^<]*)</ul>', r'\1'),
                    (r'<ol[^>]*>([^<]*)</ol>', r'\1'),
                    (r'<li[^>]*>([^<]*)</li>', r'- \1'),
                ],
                'paragraphs': (r'<p[^>]*>([^<]*)</p>', r'\1\n'),
                'images': (r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]+)"[^>]*/>', r'![\2](\1)'),
                'code': (r'<code[^>]*>([^<]*)</code>', r'`\1`'),
                'pre': (r'<pre[^>]*>([^<]*)</pre>', r'```\n\1\n```'),
            }
        }

    def get_supported_conversions(self):
        return {
            'js_to_python': ('js', 'py'),
            'python_to_js': ('py', 'js'),
            'html_to_md': ('html', 'md')
        }

    def convert_code(self, source_file, target_language):
        try:
            source_lang = self._get_language_from_ext(source_file)
            if not source_lang:
                raise ValueError(f"Could not determine source language from file extension: {source_file}")

            conversion_key = f"{source_lang}_to_{target_language}"
            if conversion_key not in self.language_patterns:
                raise ValueError(f"Unsupported conversion: {conversion_key}")

            with open(source_file, 'r', encoding='utf-8') as f:
                code = f.read()

            if conversion_key == 'js_to_python':
                converted_code = self._js_to_python(code)
            elif conversion_key == 'python_to_js':
                converted_code = self._python_to_js(code)
            elif conversion_key == 'html_to_md':
                converted_code = self._html_to_markdown(code)
            else:
                raise ValueError(f"Unsupported conversion: {conversion_key}")

            return converted_code

        except Exception as e:
            self.logger.error(f"Error converting code: {str(e)}")
            raise

    def _get_language_from_ext(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        ext_map = {
            '.js': 'js',
            '.py': 'python',
            '.html': 'html'
        }
        return ext_map.get(ext)

    def _js_to_python(self, code):
        result = code

        # First pass: Convert functions and blocks
        result = re.sub(self.language_patterns['js_to_python']['function'][0],
                       self.language_patterns['js_to_python']['function'][1], result)

        # Second pass: Convert variables and syntax
        for pattern_name, pattern in self.language_patterns['js_to_python'].items():
            if pattern_name in ['array_methods', 'operators', 'string_methods', 'undefined_null']:
                continue
            if isinstance(pattern, tuple):
                result = re.sub(pattern[0], pattern[1], result)

        # Handle array methods
        for method, pattern in self.language_patterns['js_to_python']['array_methods'].items():
            result = re.sub(pattern[0], pattern[1], result)

        # Handle operators
        for op, replacement in self.language_patterns['js_to_python']['operators'].items():
            result = result.replace(op, replacement)

        # Handle string methods
        for method, replacement in self.language_patterns['js_to_python']['string_methods'].items():
            result = re.sub(r'\.' + method + '(', '.' + replacement + '(', result)

        # Handle undefined and null
        for js_val, py_val in self.language_patterns['js_to_python']['undefined_null'].items():
            result = result.replace(js_val, py_val)

        # Clean up any remaining JavaScript artifacts
        result = re.sub(r'\{\s*\n', ':', result)  # Replace block start
        result = re.sub(r'\n\s*\}', '', result)  # Remove block end
        result = re.sub(r';\s*\n', '\n', result)  # Remove semicolons
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)  # Remove extra blank lines

        # Fix indentation
        lines = result.split('\n')
        fixed_lines = []
        indent_level = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.endswith(':'):  # Python block start
                fixed_lines.append('    ' * indent_level + stripped_line)
                indent_level += 1
            elif stripped_line.startswith('return '):  # Handle return statements
                fixed_lines.append('    ' * (indent_level) + stripped_line)
            elif stripped_line:  # Non-empty lines
                fixed_lines.append('    ' * indent_level + stripped_line)
            else:  # Empty lines
                fixed_lines.append('')

        return '\n'.join(fixed_lines)

    def _python_to_js(self, code):
        result = code
        for pattern_name, pattern in self.language_patterns['python_to_js'].items():
            if isinstance(pattern, tuple):
                result = re.sub(pattern[0], pattern[1], result)
            elif isinstance(pattern, dict):
                for method, (old, new) in pattern.items():
                    result = re.sub(old, new, result)
            else:
                result = result.replace(pattern_name, pattern)
        return result

    def _html_to_markdown(self, code):
        result = code
        for pattern_type, patterns in self.language_patterns['html_to_md'].items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    result = re.sub(pattern[0], pattern[1], result)
            else:
                result = re.sub(patterns[0], patterns[1], result)
        return result