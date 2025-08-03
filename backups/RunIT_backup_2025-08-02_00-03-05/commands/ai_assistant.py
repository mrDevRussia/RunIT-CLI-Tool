"""
AI Assistant Module for RunIT CLI Tool (Phase 2).
Provides basic offline AI assistance for code-related queries.
"""

import os
import re
import json
from pathlib import Path
from utils.file_utils import FileUtils
from utils.lang_utils import LanguageUtils
from utils.logger import Logger


class AIAssistant:
    """
    Basic AI Assistant for RunIT that provides offline code help and suggestions.
    This is a simple pattern-matching system, not a full LLM.
    """

    def __init__(self):
        """Initialize the AI Assistant with knowledge base."""
        self.file_utils = FileUtils()
        self.lang_utils = LanguageUtils()
        self.logger = Logger()
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self):
        """
        Load the built-in knowledge base for code assistance.
        
        Returns:
            dict: Knowledge base with patterns and responses
        """
        return {
            'python': {
                'patterns': {
                    r'\bfunction\b|\bdef\b': {
                        'topic': 'Python Functions',
                        'advice': """
To create a function in Python:

def function_name(parameters):
    \"\"\"Docstring describing the function\"\"\"
    # Function body
    return result

Example:
def greet(name):
    \"\"\"Greet a person by name\"\"\"
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)
""",
                        'tips': [
                            "Use descriptive function names",
                            "Add docstrings to document your functions",
                            "Keep functions focused on a single task",
                            "Use type hints for better code clarity"
                        ]
                    },
                    r'\bclass\b': {
                        'topic': 'Python Classes',
                        'advice': """
To create a class in Python:

class ClassName:
    \"\"\"Class docstring\"\"\"
    
    def __init__(self, parameters):
        \"\"\"Constructor method\"\"\"
        self.attribute = parameters
    
    def method_name(self):
        \"\"\"Method to perform an action\"\"\"
        return self.attribute

Example:
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old"

# Create an instance
person = Person("Alice", 30)
print(person.introduce())
""",
                        'tips': [
                            "Use CamelCase for class names",
                            "Always include __init__ method",
                            "Use self as the first parameter in methods",
                            "Follow the Single Responsibility Principle"
                        ]
                    },
                    r'\bloop\b|\bfor\b|\bwhile\b': {
                        'topic': 'Python Loops',
                        'advice': """
Python loop examples:

# For loop with range
for i in range(5):
    print(f"Number: {i}")

# For loop with list
items = ['apple', 'banana', 'cherry']
for item in items:
    print(f"Fruit: {item}")

# While loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1

# Loop with enumerate for index and value
for index, value in enumerate(items):
    print(f"{index}: {value}")
""",
                        'tips': [
                            "Use for loops for known iterations",
                            "Use while loops for condition-based iterations",
                            "Use enumerate() when you need both index and value",
                            "Consider list comprehensions for simple transformations"
                        ]
                    },
                    r'\berror\b|\bexception\b|\btry\b': {
                        'topic': 'Python Error Handling',
                        'advice': """
Handle errors gracefully in Python:

try:
    # Code that might raise an exception
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
    result = 0
except Exception as e:
    print(f"Unexpected error: {e}")
    result = None
else:
    print("No errors occurred")
finally:
    print("This always executes")

# Specific exception handling
try:
    with open('file.txt', 'r') as file:
        content = file.read()
except FileNotFoundError:
    print("File not found")
except PermissionError:
    print("Permission denied")
""",
                        'tips': [
                            "Catch specific exceptions when possible",
                            "Use finally for cleanup code",
                            "Don't ignore exceptions silently",
                            "Log errors for debugging"
                        ]
                    }
                }
            },
            'javascript': {
                'patterns': {
                    r'\bfunction\b': {
                        'topic': 'JavaScript Functions',
                        'advice': """
JavaScript function examples:

// Function declaration
function greet(name) {
    return `Hello, ${name}!`;
}

// Arrow function
const greet = (name) => {
    return `Hello, ${name}!`;
};

// Short arrow function
const greet = name => `Hello, ${name}!`;

// Function with default parameters
function greet(name = 'World') {
    return `Hello, ${name}!`;
}

// Calling functions
console.log(greet('Alice'));
""",
                        'tips': [
                            "Use arrow functions for short expressions",
                            "Provide default parameters when appropriate",
                            "Use descriptive function names",
                            "Consider async/await for asynchronous operations"
                        ]
                    },
                    r'\basync\b|\bawait\b|\bpromise\b': {
                        'topic': 'JavaScript Async/Await',
                        'advice': """
Handle asynchronous operations:

// Using async/await
async function fetchData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

// Using Promises
function fetchData() {
    return fetch('https://api.example.com/data')
        .then(response => response.json())
        .catch(error => {
            console.error('Error:', error);
            throw error;
        });
}

// Usage
fetchData()
    .then(data => console.log(data))
    .catch(error => console.error(error));
""",
                        'tips': [
                            "Use async/await for cleaner code",
                            "Always handle errors with try/catch",
                            "Return promises from async functions",
                            "Avoid callback hell with proper async patterns"
                        ]
                    }
                }
            },
            'general': {
                'patterns': {
                    r'\bbug\b|\berror\b|\bdebug\b': {
                        'topic': 'Debugging Tips',
                        'advice': """
General debugging strategies:

1. Read error messages carefully
2. Use print statements or console.log for tracing
3. Check variable values at different points
4. Verify input data and types
5. Use a debugger or IDE tools
6. Simplify the problem by testing smaller parts
7. Check documentation and examples
8. Search for similar issues online

Common debugging tools:
- Print/console.log statements
- IDE debugger
- Code linting tools
- Unit tests
- Error logging
""",
                        'tips': [
                            "Reproduce the bug consistently",
                            "Isolate the problem area",
                            "Check recent changes",
                            "Use version control to compare working versions"
                        ]
                    },
                    r'\bperformance\b|\boptimize\b|\bslow\b': {
                        'topic': 'Performance Optimization',
                        'advice': """
General performance optimization tips:

1. Profile your code to find bottlenecks
2. Use appropriate data structures
3. Minimize unnecessary loops and operations
4. Cache expensive computations
5. Use lazy loading when possible
6. Optimize database queries
7. Compress and minify resources
8. Use CDNs for static content

Language-specific optimizations:
- Python: Use list comprehensions, avoid global variables
- JavaScript: Minimize DOM manipulation, use requestAnimationFrame
- General: Profile first, optimize second
""",
                        'tips': [
                            "Measure before and after optimization",
                            "Focus on the biggest performance gains first",
                            "Don't optimize prematurely",
                            "Consider readability vs. performance trade-offs"
                        ]
                    }
                }
            }
        }

    def get_code_assistance(self, query, context=None):
        """
        Provide AI assistance for code-related queries.
        
        Args:
            query (str): User's question or code snippet
            context (str): Optional context like file type or language
            
        Returns:
            dict: AI response with advice and suggestions
        """
        query_lower = query.lower()
        detected_language = self._detect_language_from_query(query, context)
        
        # Search for matching patterns
        matches = []
        
        # Check language-specific patterns
        if detected_language in self.knowledge_base:
            for pattern, info in self.knowledge_base[detected_language]['patterns'].items():
                if re.search(pattern, query_lower):
                    matches.append(info)
        
        # Check general patterns
        for pattern, info in self.knowledge_base['general']['patterns'].items():
            if re.search(pattern, query_lower):
                matches.append(info)
        
        if matches:
            # Return the best match (first one for now)
            response = matches[0].copy()
            response['language'] = detected_language
            response['confidence'] = 'high' if detected_language != 'unknown' else 'medium'
        else:
            # Provide general programming advice
            response = self._get_general_advice(query)
        
        return response

    def _detect_language_from_query(self, query, context):
        """
        Detect programming language from query and context.
        
        Args:
            query (str): User's query
            context (str): Additional context
            
        Returns:
            str: Detected language or 'unknown'
        """
        query_lower = query.lower()
        
        # Check context first (like file extension)
        if context:
            lang_info = self.lang_utils.detect_language_from_extension(context)
            if lang_info:
                return lang_info['name'].lower()
        
        # Language keywords detection
        language_indicators = {
            'python': ['python', 'def ', 'import ', 'class ', '__init__', 'self.', 'print('],
            'javascript': ['javascript', 'js', 'function ', 'const ', 'let ', 'var ', 'console.log', '=>'],
            'java': ['java', 'public class', 'public static void main', 'System.out'],
            'c': ['#include', 'int main', 'printf(', 'malloc('],
            'cpp': ['c++', 'std::', '#include <iostream>', 'cout <<'],
            'html': ['html', '<html>', '<div>', '<script>', '<!DOCTYPE'],
            'css': ['css', 'background:', 'color:', 'margin:', 'padding:']
        }
        
        for language, indicators in language_indicators.items():
            for indicator in indicators:
                if indicator in query_lower:
                    return language
        
        return 'unknown'

    def _get_general_advice(self, query):
        """
        Provide general programming advice when no specific pattern matches.
        
        Args:
            query (str): User's query
            
        Returns:
            dict: General advice response
        """
        return {
            'topic': 'General Programming Help',
            'advice': f"""
I noticed you're asking about: "{query}"

Here are some general programming tips:

1. **Break Down the Problem**: Divide complex problems into smaller, manageable parts
2. **Use Descriptive Names**: Choose clear variable and function names
3. **Write Comments**: Document your code for future reference
4. **Test Frequently**: Test your code as you write it
5. **Read Documentation**: Check official docs for the language/library you're using
6. **Practice Regularly**: The best way to improve is by coding consistently

For more specific help, try asking about:
- A particular programming language (Python, JavaScript, etc.)
- Specific concepts (functions, loops, classes, etc.)
- Error messages you're encountering
- Performance optimization
- Debugging techniques

You can also use RunIT's other commands:
- `create <language> <filename>` to generate boilerplate code
- `scan <filename>` to check for potential issues
- `info <filename>` to analyze existing code
""",
            'tips': [
                "Be specific in your questions",
                "Provide code examples when possible",
                "Mention the programming language you're using",
                "Include any error messages you're seeing"
            ],
            'language': 'general',
            'confidence': 'low'
        }

    def format_ai_response(self, response):
        """
        Format AI response for display.
        
        Args:
            response (dict): AI response data
        """
        print(f"\n🤖 AI Assistant - {response['topic']}")
        print("=" * 60)
        
        print("📚 Advice:")
        print(response['advice'])
        
        if 'tips' in response:
            print("\n💡 Tips:")
            for tip in response['tips']:
                print(f"   • {tip}")
        
        print(f"\n🔍 Language: {response.get('language', 'general').title()}")
        print(f"📊 Confidence: {response.get('confidence', 'medium').title()}")
        
        print("\n" + "=" * 60)
        print("💭 This is basic offline AI assistance. For complex issues,")
        print("   consider consulting official documentation or online resources.")

    def help_with_file(self, filename):
        """
        Provide AI assistance based on a specific file.
        
        Args:
            filename (str): Name of the file to analyze
        """
        try:
            file_path = Path(filename)
            if not file_path.exists():
                print(f"❌ File '{filename}' not found")
                return
            
            # Detect language from file extension
            extension = file_path.suffix.lower()
            lang_info = self.lang_utils.detect_language_from_extension(extension)
            
            if not lang_info:
                print(f"⚠️ Unsupported file type: {extension}")
                return
            
            # Read file content (first 50 lines for analysis)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:50]
                    content = ''.join(lines)
            except Exception as e:
                print(f"❌ Could not read file: {e}")
                return
            
            # Analyze content and provide suggestions
            language = lang_info['name'].lower()
            response = {
                'topic': f'{lang_info["name"]} File Analysis',
                'advice': f"""
File: {filename}
Language: {lang_info['name']}
Extension: {extension}

Based on your {language} file, here are some suggestions:

📝 Code Quality:
- Ensure proper indentation and formatting
- Add comments to explain complex logic
- Use meaningful variable and function names
- Follow {language} coding conventions

🔍 What I noticed:
- File has {len(lines)} lines analyzed
- Language: {lang_info['name']}
""",
                'tips': [
                    f"Use RunIT's 'info {filename}' for detailed file statistics",
                    f"Use RunIT's 'scan {filename}' to check for issues",
                    f"Use RunIT's 'run {filename}' to test execution",
                    "Consider adding error handling and validation"
                ],
                'language': language,
                'confidence': 'high'
            }
            
            # Add language-specific advice
            if language in self.knowledge_base:
                response['advice'] += f"\n\n🎯 {lang_info['name']}-specific tips:\n"
                for pattern_info in self.knowledge_base[language]['patterns'].values():
                    response['advice'] += f"- {pattern_info['tips'][0]}\n"
            
            self.format_ai_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI file analysis: {e}")
            print(f"❌ Error analyzing file: {e}")

    def show_ai_help(self):
        """Show help for the AI assistant."""
        help_text = """
🤖 RunIT AI Assistant (Offline Mode)

DESCRIPTION:
   Basic offline AI assistance for programming and code-related questions.
   Uses pattern matching and built-in knowledge base.

USAGE:
   In RunIT interactive mode, use: runai <query>

EXAMPLES:
   runai How do I create a function in Python?
   runai JavaScript async await example
   runai Help me debug this error
   runai What's the best way to handle exceptions?
   runai file:example.py                    # Analyze specific file

SUPPORTED TOPICS:
   • Python: functions, classes, loops, error handling
   • JavaScript: functions, async/await, promises
   • General: debugging, performance, best practices
   • File analysis: code quality suggestions

LIMITATIONS:
   ⚠️  This is basic offline assistance, not a full AI model
   • Limited to built-in knowledge patterns
   • Cannot browse the internet or access external resources
   • For complex problems, consult official documentation

TIPS:
   • Be specific in your questions
   • Mention the programming language
   • Include error messages if applicable
   • Use other RunIT commands for detailed analysis
"""
        print(help_text)