"""
File Searcher Module for RunIT CLI Tool.
Handles keyword search within files with context and line numbers.
"""

import re
from pathlib import Path
from utils.file_utils import FileUtils
from utils.logger import Logger


class FileSearcher:
    """
    Handles searching for keywords within files and displaying results
    with line numbers and context.
    """

    def __init__(self):
        """Initialize the FileSearcher with utilities."""
        self.file_utils = FileUtils()
        self.logger = Logger()

    def search_in_content(self, keyword, content, case_sensitive=False, whole_word=False):
        """
        Search for keyword in content and return matches with line information.
        
        Args:
            keyword (str): Keyword to search for
            content (str): Content to search in
            case_sensitive (bool): Whether search should be case sensitive
            whole_word (bool): Whether to match whole words only
            
        Returns:
            list: List of match dictionaries with line info
        """
        matches = []
        lines = content.split('\n')
        
        # Prepare search pattern
        if whole_word:
            pattern = r'\b' + re.escape(keyword) + r'\b'
        else:
            pattern = re.escape(keyword)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            return [{'error': f"Invalid search pattern: {e}"}]
        
        # Search through each line
        for line_num, line in enumerate(lines, 1):
            line_matches = list(compiled_pattern.finditer(line))
            
            for match in line_matches:
                matches.append({
                    'line_number': line_num,
                    'line_content': line,
                    'match_start': match.start(),
                    'match_end': match.end(),
                    'matched_text': match.group(),
                    'before_match': line[:match.start()],
                    'after_match': line[match.end():]
                })
        
        return matches

    def get_context_lines(self, content, target_line, context_size=2):
        """
        Get context lines around a target line.
        
        Args:
            content (str): Full file content
            target_line (int): Target line number (1-based)
            context_size (int): Number of lines before and after to include
            
        Returns:
            dict: Context information with before, target, and after lines
        """
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Convert to 0-based indexing
        target_idx = target_line - 1
        
        # Calculate context range
        start_idx = max(0, target_idx - context_size)
        end_idx = min(total_lines, target_idx + context_size + 1)
        
        context = {
            'before_lines': [],
            'target_line': {
                'number': target_line,
                'content': lines[target_idx] if 0 <= target_idx < total_lines else ''
            },
            'after_lines': [],
            'start_line_number': start_idx + 1,
            'end_line_number': end_idx
        }
        
        # Add before lines
        for i in range(start_idx, target_idx):
            context['before_lines'].append({
                'number': i + 1,
                'content': lines[i]
            })
        
        # Add after lines
        for i in range(target_idx + 1, end_idx):
            context['after_lines'].append({
                'number': i + 1,
                'content': lines[i]
            })
        
        return context

    def highlight_matches_in_line(self, line, matches, highlight_char='►'):
        """
        Add visual highlighting to matches in a line.
        
        Args:
            line (str): Line content
            matches (list): List of match objects for this line
            highlight_char (str): Character to use for highlighting
            
        Returns:
            str: Line with highlighted matches
        """
        if not matches:
            return line
        
        # Sort matches by position (reverse order for replacement)
        sorted_matches = sorted(matches, key=lambda m: m['match_start'], reverse=True)
        
        highlighted_line = line
        for match in sorted_matches:
            start = match['match_start']
            end = match['match_end']
            match_text = match['matched_text']
            
            # Replace match with highlighted version
            highlighted_match = f"{highlight_char}{match_text}{highlight_char}"
            highlighted_line = highlighted_line[:start] + highlighted_match + highlighted_line[end:]
        
        return highlighted_line

    def format_search_results(self, filename, keyword, matches, total_lines, show_context=True):
        """
        Format and display search results.
        
        Args:
            filename (str): Name of searched file
            keyword (str): Search keyword
            matches (list): List of matches
            total_lines (int): Total lines in file
            show_context (bool): Whether to show context lines
        """
        print(f"\n🔍 Search Results for '{keyword}' in: {filename}")
        print("=" * 60)
        
        if not matches:
            print("❌ No matches found")
            return
        
        # Check for errors
        if matches and 'error' in matches[0]:
            print(f"❌ {matches[0]['error']}")
            return
        
        print(f"✅ Found {len(matches)} match(es) in {total_lines} lines")
        print("-" * 60)
        
        # Group matches by line number
        matches_by_line = {}
        for match in matches:
            line_num = match['line_number']
            if line_num not in matches_by_line:
                matches_by_line[line_num] = []
            matches_by_line[line_num].append(match)
        
        # Display results
        for line_num in sorted(matches_by_line.keys()):
            line_matches = matches_by_line[line_num]
            first_match = line_matches[0]
            
            print(f"\n📍 Line {line_num}:")
            
            # Show the line with highlighting
            highlighted_line = self.highlight_matches_in_line(
                first_match['line_content'], 
                line_matches
            )
            
            print(f"   {highlighted_line}")
            
            # Show match details if multiple matches on same line
            if len(line_matches) > 1:
                print(f"   └─ {len(line_matches)} matches on this line")
            
            # Show character positions
            positions = [f"pos {m['match_start']}-{m['match_end']}" for m in line_matches]
            print(f"   └─ Match positions: {', '.join(positions)}")

    def search_in_file(self, keyword, filename, case_sensitive=False, whole_word=False, show_context=True):
        """
        Main method to search for a keyword in a file.
        
        Args:
            keyword (str): Keyword to search for
            filename (str): Name or path of the file to search
            case_sensitive (bool): Whether search should be case sensitive
            whole_word (bool): Whether to match whole words only
            show_context (bool): Whether to show context lines
        """
        try:
            # Validate inputs
            if not keyword:
                print("❌ Error: Search keyword cannot be empty")
                return
            
            if not keyword.strip():
                print("❌ Error: Search keyword cannot be just whitespace")
                return
            
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
            
            # Get file info
            file_size = self.file_utils.get_file_size(file_path)
            
            # Check file size (avoid searching very large files)
            if file_path.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
                print(f"⚠️  File '{filename}' is very large ({file_size})")
                response = input("Continue searching? This may take a while (y/n): ").lower()
                if response not in ['y', 'yes']:
                    print("❌ Search cancelled")
                    return
            
            self.logger.info(f"Searching for '{keyword}' in: {file_path}")
            
            # Read file content
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
                    print(f"❌ Unable to read file '{filename}' with any supported encoding")
                    return
            
            # Perform search
            matches = self.search_in_content(keyword, content, case_sensitive, whole_word)
            total_lines = len(content.split('\n'))
            
            # Format and display results
            self.format_search_results(filename, keyword, matches, total_lines, show_context)
            
            # Log results
            if matches and 'error' not in matches[0]:
                self.logger.info(f"Search completed: {len(matches)} matches found in {file_path}")
            else:
                self.logger.info(f"Search completed: no matches found in {file_path}")
            
        except PermissionError:
            print(f"❌ Permission denied: Cannot read file '{filename}'")
        except Exception as e:
            self.logger.error(f"Error searching in file {filename}: {e}")
            print(f"❌ Error searching file: {e}")

    def search_multiple_keywords(self, keywords, filename):
        """
        Search for multiple keywords in a file.
        
        Args:
            keywords (list): List of keywords to search for
            filename (str): Name or path of the file to search
        """
        if not keywords:
            print("❌ No keywords provided")
            return
        
        print(f"🔍 Searching for {len(keywords)} keywords in: {filename}")
        print("-" * 60)
        
        total_matches = 0
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] Searching for: '{keyword}'")
            self.search_in_file(keyword, filename, show_context=False)
            
            # Add separator between searches
            if i < len(keywords):
                print("\n" + "-" * 40)

    def get_search_statistics(self, filename):
        """
        Get basic statistics about a file for search purposes.
        
        Args:
            filename (str): Name or path of the file
            
        Returns:
            dict: File statistics
        """
        try:
            file_path = Path(filename).resolve()
            
            if not file_path.exists() or not file_path.is_file():
                return None
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            words = content.split()
            
            return {
                'total_lines': len(lines),
                'total_words': len(words),
                'total_characters': len(content),
                'file_size': self.file_utils.get_file_size(file_path),
                'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
            }
            
        except Exception:
            return None
