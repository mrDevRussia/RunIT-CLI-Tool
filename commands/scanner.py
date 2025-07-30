"""
Virus Scanner Module for RunIT CLI Tool.
Performs local pattern-based detection of suspicious code patterns.
"""

import re
import base64
import binascii
from pathlib import Path
from utils.file_utils import FileUtils
from utils.logger import Logger


class VirusScanner:
    """
    Local virus scanner that detects suspicious patterns in code files.
    This is a basic pattern-matching scanner, not a comprehensive antivirus.
    """

    def __init__(self):
        """Initialize the VirusScanner with utilities and patterns."""
        self.file_utils = FileUtils()
        self.logger = Logger()
        self.init_detection_patterns()

    def init_detection_patterns(self):
        """Initialize suspicious code patterns for detection."""
        
        # Suspicious function calls and patterns
        self.suspicious_patterns = {
            'eval_functions': {
                'patterns': [
                    r'\beval\s*\(',
                    r'\bexec\s*\(',
                    r'__import__\s*\(',
                    r'getattr\s*\(',
                    r'setattr\s*\(',
                    r'execfile\s*\(',
                    r'compile\s*\(',
                ],
                'description': 'Dynamic code execution functions',
                'risk': 'HIGH'
            },
            
            'obfuscation': {
                'patterns': [
                    r'[A-Za-z0-9+/]{50,}={0,2}',  # Base64-like strings
                    r'\\x[0-9a-fA-F]{2}',         # Hex encoded strings
                    r'chr\s*\(\s*\d+\s*\)',       # Character code obfuscation
                    r'ord\s*\(',                  # Character to code conversion
                    r'decode\s*\([\'"].*?[\'"].*?\)',  # Decoding operations
                ],
                'description': 'Code obfuscation techniques',
                'risk': 'MEDIUM'
            },
            
            'system_access': {
                'patterns': [
                    r'os\.system\s*\(',
                    r'subprocess\.',
                    r'shell=True',
                    r'Popen\s*\(',
                    r'call\s*\(',
                    r'run\s*\(',
                    r'cmd\s*/c',
                    r'powershell',
                    r'system\s*\(',
                ],
                'description': 'System command execution',
                'risk': 'MEDIUM'
            },
            
            'network_activity': {
                'patterns': [
                    r'urllib\.request',
                    r'requests\.',
                    r'http\.client',
                    r'socket\.',
                    r'connect\s*\(',
                    r'bind\s*\(',
                    r'listen\s*\(',
                    r'accept\s*\(',
                    r'send\s*\(',
                    r'recv\s*\(',
                ],
                'description': 'Network communication',
                'risk': 'LOW'
            },
            
            'file_operations': {
                'patterns': [
                    r'open\s*\([^)]*[\'"]w[\'"]',
                    r'\.write\s*\(',
                    r'\.writelines\s*\(',
                    r'shutil\.',
                    r'os\.remove',
                    r'os\.unlink',
                    r'os\.rmdir',
                    r'rmtree\s*\(',
                ],
                'description': 'File system modifications',
                'risk': 'LOW'
            },
            
            'crypto_operations': {
                'patterns': [
                    r'hashlib\.',
                    r'crypt\.',
                    r'Crypto\.',
                    r'cryptography\.',
                    r'encrypt\s*\(',
                    r'decrypt\s*\(',
                    r'AES\.',
                    r'RSA\.',
                ],
                'description': 'Cryptographic operations',
                'risk': 'LOW'
            },
            
            'suspicious_keywords': {
                'patterns': [
                    r'\bkeylogger\b',
                    r'\bmalware\b',
                    r'\btrojan\b',
                    r'\bvirus\b',
                    r'\bbackdoor\b',
                    r'\brootkit\b',
                    r'\bransomware\b',
                    r'\bstealer\b',
                ],
                'description': 'Suspicious keywords',
                'risk': 'HIGH'
            }
        }

    def check_base64_content(self, content):
        """
        Check for suspicious base64 encoded content.
        
        Args:
            content (str): File content to check
            
        Returns:
            list: List of suspicious findings
        """
        findings = []
        
        # Find potential base64 strings
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.finditer(base64_pattern, content)
        
        for match in matches:
            b64_string = match.group()
            try:
                # Try to decode base64
                decoded = base64.b64decode(b64_string, validate=True)
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                # Check if decoded content contains suspicious patterns
                suspicious_decoded = any([
                    'eval(' in decoded_str,
                    'exec(' in decoded_str,
                    'system(' in decoded_str,
                    'shell' in decoded_str.lower(),
                    'cmd' in decoded_str.lower(),
                ])
                
                if suspicious_decoded:
                    findings.append({
                        'type': 'base64_suspicious',
                        'line': content[:match.start()].count('\n') + 1,
                        'content': b64_string[:50] + '...' if len(b64_string) > 50 else b64_string,
                        'decoded_preview': decoded_str[:100] + '...' if len(decoded_str) > 100 else decoded_str,
                        'risk': 'HIGH'
                    })
                    
            except (base64.binascii.Error, UnicodeDecodeError):
                # Not valid base64 or not UTF-8 text
                continue
                
        return findings

    def scan_content(self, content):
        """
        Scan file content for suspicious patterns.
        
        Args:
            content (str): File content to scan
            
        Returns:
            dict: Scan results with findings
        """
        findings = []
        
        # Check regular suspicious patterns
        for category, info in self.suspicious_patterns.items():
            for pattern in info['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    line_content = content[line_start:line_end].strip()
                    
                    findings.append({
                        'type': category,
                        'pattern': pattern,
                        'line': line_num,
                        'content': line_content,
                        'match': match.group(),
                        'description': info['description'],
                        'risk': info['risk']
                    })
        
        # Check for base64 suspicious content
        base64_findings = self.check_base64_content(content)
        findings.extend(base64_findings)
        
        return findings

    def calculate_risk_score(self, findings):
        """
        Calculate overall risk score based on findings.
        
        Args:
            findings (list): List of scan findings
            
        Returns:
            tuple: (risk_score, risk_level)
        """
        risk_weights = {'HIGH': 10, 'MEDIUM': 5, 'LOW': 1}
        total_score = sum(risk_weights.get(finding.get('risk', 'LOW'), 1) for finding in findings)
        
        if total_score >= 20:
            risk_level = 'HIGH'
        elif total_score >= 10:
            risk_level = 'MEDIUM'
        elif total_score > 0:
            risk_level = 'LOW'
        else:
            risk_level = 'CLEAN'
            
        return total_score, risk_level

    def format_scan_results(self, filename, findings, file_size, scan_time):
        """
        Format and display scan results.
        
        Args:
            filename (str): Name of scanned file
            findings (list): List of scan findings
            file_size (str): File size string
            scan_time (float): Scan duration in seconds
        """
        risk_score, risk_level = self.calculate_risk_score(findings)
        
        # Header
        print(f"\n🔍 Virus Scan Results for: {filename}")
        print("=" * 60)
        print(f"📁 File Size: {file_size}")
        print(f"⏱️  Scan Time: {scan_time:.2f} seconds")
        print(f"🎯 Risk Score: {risk_score}")
        
        # Risk level with color coding (text-based)
        risk_indicators = {
            'CLEAN': '✅ CLEAN',
            'LOW': '🟡 LOW RISK',
            'MEDIUM': '🟠 MEDIUM RISK', 
            'HIGH': '🔴 HIGH RISK'
        }
        
        print(f"⚠️  Risk Level: {risk_indicators.get(risk_level, 'UNKNOWN')}")
        print("-" * 60)
        
        if not findings:
            print("✅ No suspicious patterns detected.")
            print("📝 Note: This is a basic pattern scanner. Use comprehensive antivirus for thorough protection.")
            return
        
        # Group findings by risk level
        findings_by_risk = {}
        for finding in findings:
            risk = finding.get('risk', 'LOW')
            if risk not in findings_by_risk:
                findings_by_risk[risk] = []
            findings_by_risk[risk].append(finding)
        
        # Display findings by risk level
        for risk in ['HIGH', 'MEDIUM', 'LOW']:
            if risk in findings_by_risk:
                risk_findings = findings_by_risk[risk]
                print(f"\n{risk_indicators.get(risk, risk)} ({len(risk_findings)} findings):")
                
                for i, finding in enumerate(risk_findings, 1):
                    print(f"\n  {i}. {finding.get('description', 'Unknown')}")
                    print(f"     Line {finding.get('line', 'N/A')}: {finding.get('content', '')[:80]}...")
                    
                    if 'decoded_preview' in finding:
                        print(f"     Decoded: {finding['decoded_preview']}")
                    
                    if finding.get('match'):
                        print(f"     Pattern: {finding['match']}")
        
        print("\n" + "=" * 60)
        print("⚠️  DISCLAIMER: This is a basic pattern-based scanner.")
        print("   For comprehensive protection, use professional antivirus software.")
        print("   Always review code manually before execution.")

    def scan_file(self, filename):
        """
        Main method to scan a file for viruses and suspicious patterns.
        
        Args:
            filename (str): Name or path of the file to scan
        """
        import time
        
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
            
            # Get file info
            file_size = self.file_utils.get_file_size(file_path)
            
            # Check file size (avoid scanning very large files)
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                print(f"⚠️  File '{filename}' is very large ({file_size})")
                response = input("Continue scanning? This may take a while (y/n): ").lower()
                if response not in ['y', 'yes']:
                    print("❌ Scan cancelled")
                    return
            
            self.logger.info(f"Starting virus scan: {file_path}")
            start_time = time.time()
            
            print(f"🔍 Scanning {filename} for suspicious patterns...")
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try binary mode for non-text files
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                    content = raw_content.decode('utf-8', errors='ignore')
            
            # Perform scan
            findings = self.scan_content(content)
            scan_time = time.time() - start_time
            
            # Format and display results
            self.format_scan_results(filename, findings, file_size, scan_time)
            
            self.logger.info(f"Virus scan completed: {file_path} - {len(findings)} findings")
            
        except PermissionError:
            print(f"❌ Permission denied: Cannot read file '{filename}'")
        except Exception as e:
            self.logger.error(f"Error scanning file {filename}: {e}")
            print(f"❌ Error scanning file: {e}")

    def get_scan_statistics(self):
        """
        Return statistics about the scanner's capabilities.
        
        Returns:
            dict: Scanner statistics
        """
        total_patterns = sum(len(info['patterns']) for info in self.suspicious_patterns.values())
        
        return {
            'pattern_categories': len(self.suspicious_patterns),
            'total_patterns': total_patterns,
            'supported_features': [
                'Dynamic code execution detection',
                'Code obfuscation detection', 
                'System access monitoring',
                'Network activity detection',
                'File operation monitoring',
                'Cryptographic operation detection',
                'Base64 content analysis',
                'Suspicious keyword detection'
            ]
        }
