#!/usr/bin/env python3
"""
Aegis Vanguard Package for RunIT

Provides functionality to scan websites for security vulnerabilities and generate reports.

Version: 1.0.0
License: MIT
"""

import os
import sys
import json
import re
import datetime
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

# Try to import optional dependencies
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    print("Warning: colorama not installed. Output will not be colored.")
    print("Install with: pip install colorama")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Warning: reportlab not installed. PDF reports will not be available.")
    print("Install with: pip install reportlab")

try:
    import jinja2
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False
    print("Warning: jinja2 not installed. HTML reports will not be available.")
    print("Install with: pip install jinja2")

# Global instance
_av_instance = None

def handle_command(command: str, args: List[str]) -> bool:
    """Global handle_command function required by RunIT."""
    global _av_instance
    if _av_instance is None:
        _av_instance = AegisVanguard()
    return _av_instance.handle_command(command, args)

class Vulnerability:
    """Represents a security vulnerability."""
    
    def __init__(self, vuln_type: str, file_path: str, line_number: int, severity: str, description: str, fix: str):
        self.vuln_type = vuln_type
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.description = description
        self.fix = fix

class AegisVanguard:
    """Manages website security scanning for RunIT."""

    def __init__(self):
        """Initialize the Aegis Vanguard scanner."""
        self.name = "aegis_vanguard_RunIT"
        self.version = "1.0.0"
        self.current_dir = os.getcwd()
        
        # Vulnerability patterns
        self.patterns = {
            "sql_injection": {
                # Enhanced pattern to reduce false positives by requiring user input context
                "pattern": r"(?:execute|query)\s*\(\s*['\"].*?(?:SELECT|INSERT|UPDATE|DELETE).*?['\"]\s*\+\s*(?:\w+(?:\.value|\.innerHTML|\[['\"](.*?)['\"]\])|.*?(?:GET|POST|REQUEST|COOKIE).*?)\s*\)",
                "severity": "high",
                "description": "SQL Injection vulnerability detected",
                "fix": "Use Prepared Statements or ORM instead of raw queries"
            },
            "xss": {
                # Enhanced pattern to better detect XSS vulnerabilities
                "pattern": r"(?:innerHTML|outerHTML|document\.write)\s*=\s*.*?(?:\w+\.value|\$\(.*?\)\.val\(\)|(?:GET|POST|REQUEST|COOKIE)).*?(?:\+|\$\{|\$|\`)",
                "severity": "medium",
                "description": "Cross-Site Scripting (XSS) vulnerability detected",
                "fix": "Sanitize user inputs and encode HTML output"
            },
            "file_inclusion": {
                "pattern": r"(?:include|require|include_once|require_once)\s*\(\s*\$_(?:GET|POST|REQUEST|COOKIE)\[",
                "severity": "critical",
                "description": "File Inclusion vulnerability detected",
                "fix": "Validate file paths and use whitelisting"
            },
            "weak_auth": {
                "pattern": r"(?:password|passwd|pwd)\s*=\s*['\"][^'\"]{1,8}['\"]|md5\s*\(",
                "severity": "high",
                "description": "Weak Authentication detected",
                "fix": "Use strong password hashing (bcrypt/Argon2) and enforce password policies"
            },
            "debug_mode": {
                "pattern": r"(?:debug|development)\s*[=:]\s*(?:true|1)|display_errors\s*[=:]\s*(?:On|1)",
                "severity": "low",
                "description": "Debug mode enabled in production",
                "fix": "Disable debug mode in production environments"
            },
            "csrf": {
                "pattern": r"<form[^>]*>(?:(?!csrf|token|nonce).)*?<\/form>|\$\((?:'|\")form(?:'|\")\)[^;]*\.submit\(\)",
                "severity": "high",
                "description": "Cross-Site Request Forgery (CSRF) vulnerability detected",
                "fix": "Implement anti-CSRF tokens in all forms and validate them on form submission"
            },
            "idor": {
                "pattern": r"(?:user_?id|account_?id|profile_?id|order_?id)\s*=\s*(?:\$_(?:GET|POST|REQUEST|COOKIE)\[['\"](.*?)['\"]\]|\w+\.value|\w+\[['\"](.*?)['\"]\])",
                "severity": "high",
                "description": "Insecure Direct Object Reference (IDOR) vulnerability detected",
                "fix": "Implement proper access control checks and use indirect references"
            },
            "insecure_deserialization": {
                "pattern": r"(?:unserialize|deserialize|fromJSON|parse)\s*\(\s*(?:\$_(?:GET|POST|REQUEST|COOKIE)|.*?\+\s*.*?)\)",
                "severity": "critical",
                "description": "Insecure Deserialization vulnerability detected",
                "fix": "Validate and sanitize data before deserialization, use safer alternatives like JSON"
            }
        }

    def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle package commands.

        Args:
            command: The command to execute
            args: List of command arguments

        Returns:
            bool: True if command was handled successfully
        """
        if command == "av":
            return self._scan_website(args)
        return False

    def _scan_website(self, args: List[str]) -> bool:
        """Scan website folder for security vulnerabilities.

        Args:
            args: Command arguments, website folder path

        Returns:
            bool: True if command executed successfully
        """
        if not args:
            self._print_error("Please specify a website folder")
            print("Usage: av <website_folder>")
            return False

        website_folder = args[0]
        if not os.path.isdir(website_folder):
            self._print_error(f"Folder not found: {website_folder}")
            return False

        print(f"[+] Scanning website: {website_folder}")
        print("-----------------------------------")

        # Scan website files
        vulnerabilities = self._scan_files(website_folder)

        # Display results
        self._display_results(vulnerabilities)

        # Generate reports
        self._generate_reports(website_folder, vulnerabilities)

        return True

    def _scan_files(self, folder_path: str) -> List[Vulnerability]:
        """Scan files in the website folder for vulnerabilities.

        Args:
            folder_path: Path to the website folder

        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []
        extensions = [".html", ".js", ".php", ".asp", ".aspx", ".jsp", ".py", ".rb", ".xml", ".json", ".config", ".ini"]

        for root, _, files in os.walk(folder_path):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                for vuln_type, pattern_info in self.patterns.items():
                                    if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                                        vulnerabilities.append(Vulnerability(
                                            vuln_type=vuln_type,
                                            file_path=os.path.relpath(file_path, folder_path),
                                            line_number=i + 1,
                                            severity=pattern_info["severity"],
                                            description=pattern_info["description"],
                                            fix=pattern_info["fix"]
                                        ))
                    except Exception as e:
                        print(f"Error reading file {file_path}: {str(e)}")

        return vulnerabilities

    def _display_results(self, vulnerabilities: List[Vulnerability]) -> None:
        """Display scan results in the terminal.

        Args:
            vulnerabilities: List of detected vulnerabilities
        """
        if not vulnerabilities:
            self._print_success("No vulnerabilities detected")
            return

        for vuln in vulnerabilities:
            severity_color = self._get_severity_color(vuln.severity)
            print(f"[!] {severity_color}{vuln.description} in: {vuln.file_path} (Line: {vuln.line_number}) (Severity: {vuln.severity.capitalize()})")
            print(f"    ➤ Fix: {vuln.fix}")

        print("-----------------------------------")

    def _generate_reports(self, website_folder: str, vulnerabilities: List[Vulnerability]) -> None:
        """Generate reports in different formats.

        Args:
            website_folder: Path to the website folder
            vulnerabilities: List of detected vulnerabilities
        """
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_dir, exist_ok=True)

        # Generate timestamp for report filenames
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        base_filename = f"{timestamp}_report"

        # Generate JSON report
        json_report = os.path.join(reports_dir, f"{base_filename}.json")
        self._generate_json_report(json_report, website_folder, vulnerabilities)

        # Generate PDF report if reportlab is available
        if HAS_REPORTLAB:
            pdf_report = os.path.join(reports_dir, f"{base_filename}.pdf")
            self._generate_pdf_report(pdf_report, website_folder, vulnerabilities)

        # Generate HTML report if jinja2 is available
        if HAS_JINJA:
            html_report = os.path.join(reports_dir, f"{base_filename}.html")
            self._generate_html_report(html_report, website_folder, vulnerabilities)

        print(f"⚠️ Full report saved at: {os.path.join('reports', base_filename + '.json')}")
        if HAS_REPORTLAB:
            print(f"⚠️ PDF report saved at: {os.path.join('reports', base_filename + '.pdf')}")
        if HAS_JINJA:
            print(f"⚠️ HTML report saved at: {os.path.join('reports', base_filename + '.html')}")

    def _generate_json_report(self, filename: str, website_folder: str, vulnerabilities: List[Vulnerability]) -> None:
        """Generate JSON report.

        Args:
            filename: Output filename
            website_folder: Path to the website folder
            vulnerabilities: List of detected vulnerabilities
        """
        report_data = {
            "scan_date": datetime.datetime.now().isoformat(),
            "website_folder": website_folder,
            "vulnerabilities": [
                {
                    "type": vuln.vuln_type,
                    "file": vuln.file_path,
                    "line": vuln.line_number,
                    "severity": vuln.severity,
                    "description": vuln.description,
                    "fix": vuln.fix
                } for vuln in vulnerabilities
            ],
            "summary": {
                "total": len(vulnerabilities),
                "by_severity": {
                    "critical": sum(1 for v in vulnerabilities if v.severity == "critical"),
                    "high": sum(1 for v in vulnerabilities if v.severity == "high"),
                    "medium": sum(1 for v in vulnerabilities if v.severity == "medium"),
                    "low": sum(1 for v in vulnerabilities if v.severity == "low")
                }
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

    def _generate_pdf_report(self, filename: str, website_folder: str, vulnerabilities: List[Vulnerability]) -> None:
        """Generate PDF report.

        Args:
            filename: Output filename
            website_folder: Path to the website folder
            vulnerabilities: List of detected vulnerabilities
        """
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, "Aegis Vanguard Security Scan Report")

        # Scan information
        c.setFont("Helvetica", 12)
        c.drawString(72, height - 100, f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(72, height - 120, f"Website Folder: {website_folder}")

        # Summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, height - 160, "Vulnerability Summary")

        c.setFont("Helvetica", 12)
        total = len(vulnerabilities)
        critical = sum(1 for v in vulnerabilities if v.severity == "critical")
        high = sum(1 for v in vulnerabilities if v.severity == "high")
        medium = sum(1 for v in vulnerabilities if v.severity == "medium")
        low = sum(1 for v in vulnerabilities if v.severity == "low")

        c.drawString(72, height - 180, f"Total Vulnerabilities: {total}")
        c.drawString(72, height - 200, f"Critical: {critical}")
        c.drawString(72, height - 220, f"High: {high}")
        c.drawString(72, height - 240, f"Medium: {medium}")
        c.drawString(72, height - 260, f"Low: {low}")

        # Vulnerabilities
        if vulnerabilities:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(72, height - 300, "Detected Vulnerabilities")

            y_position = height - 320
            for i, vuln in enumerate(vulnerabilities):
                if y_position < 100:  # Check if we need a new page
                    c.showPage()
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(72, height - 72, "Detected Vulnerabilities (continued)")
                    y_position = height - 100

                c.setFont("Helvetica-Bold", 12)
                c.drawString(72, y_position, f"{i+1}. {vuln.description} ({vuln.severity.capitalize()})")
                y_position -= 20

                c.setFont("Helvetica", 10)
                c.drawString(90, y_position, f"File: {vuln.file_path} (Line: {vuln.line_number})")
                y_position -= 15

                c.drawString(90, y_position, f"Fix: {vuln.fix}")
                y_position -= 30
        else:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(72, height - 300, "No vulnerabilities detected")

        c.save()

    def _generate_html_report(self, filename: str, website_folder: str, vulnerabilities: List[Vulnerability]) -> None:
        """Generate HTML report.

        Args:
            filename: Output filename
            website_folder: Path to the website folder
            vulnerabilities: List of detected vulnerabilities
        """
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Aegis Vanguard Security Scan Report</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
                
                :root {
                    --primary-color: #0a192f;
                    --secondary-color: #172a45;
                    --accent-color: #64ffda;
                    --text-color: #e6f1ff;
                    --critical-color: #ff5252;
                    --high-color: #ff9100;
                    --medium-color: #ffeb3b;
                    --low-color: #4caf50;
                }
                
                body { 
                    font-family: 'Roboto Mono', monospace;
                    margin: 0;
                    padding: 0;
                    background-color: var(--primary-color);
                    color: var(--text-color);
                    line-height: 1.6;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                header {
                    background-color: var(--secondary-color);
                    padding: 20px;
                    border-bottom: 3px solid var(--accent-color);
                    position: relative;
                    overflow: hidden;
                }
                
                header::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: repeating-linear-gradient(
                        45deg,
                        transparent,
                        transparent 10px,
                        rgba(10, 25, 47, 0.1) 10px,
                        rgba(10, 25, 47, 0.1) 20px
                    );
                    z-index: 1;
                }
                
                .header-content {
                    position: relative;
                    z-index: 2;
                }
                
                h1 {
                    color: var(--accent-color);
                    margin: 0;
                    font-size: 2.5em;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    text-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
                }
                
                h2 {
                    color: var(--accent-color);
                    border-bottom: 2px solid var(--accent-color);
                    padding-bottom: 10px;
                    margin-top: 30px;
                }
                
                .info {
                    background-color: var(--secondary-color);
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid var(--accent-color);
                }
                
                .summary {
                    background-color: var(--secondary-color);
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .stat-box {
                    background-color: var(--primary-color);
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                    border: 1px solid rgba(230, 241, 255, 0.1);
                }
                
                .stat-box h3 {
                    margin: 0;
                    font-size: 0.9em;
                    text-transform: uppercase;
                }
                
                .stat-box .value {
                    font-size: 2em;
                    font-weight: bold;
                    margin: 10px 0;
                }
                
                .critical-stat { color: var(--critical-color); }
                .high-stat { color: var(--high-color); }
                .medium-stat { color: var(--medium-color); }
                .low-stat { color: var(--low-color); }
                
                .vulnerability {
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 5px;
                    background-color: var(--secondary-color);
                    border-left: 4px solid #ccc;
                    position: relative;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                
                .vulnerability::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 0;
                    height: 0;
                    border-style: solid;
                    border-width: 0 40px 40px 0;
                    border-color: transparent var(--primary-color) transparent transparent;
                }
                
                .vulnerability h3 {
                    margin-top: 0;
                    color: #fff;
                }
                
                .critical {
                    border-left-color: var(--critical-color);
                    background-color: rgba(255, 82, 82, 0.1);
                }
                
                .high {
                    border-left-color: var(--high-color);
                    background-color: rgba(255, 145, 0, 0.1);
                }
                
                .medium {
                    border-left-color: var(--medium-color);
                    background-color: rgba(255, 235, 59, 0.1);
                }
                
                .low {
                    border-left-color: var(--low-color);
                    background-color: rgba(76, 175, 80, 0.1);
                }
                
                .fix {
                    margin-top: 15px;
                    padding: 15px;
                    background-color: var(--primary-color);
                    border-radius: 5px;
                    border-left: 4px solid var(--accent-color);
                }
                
                .code {
                    font-family: 'Roboto Mono', monospace;
                    background-color: rgba(10, 25, 47, 0.5);
                    padding: 2px 5px;
                    border-radius: 3px;
                }
                
                footer {
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    background-color: var(--secondary-color);
                    border-top: 3px solid var(--accent-color);
                    font-size: 0.9em;
                }
                
                .shield-icon {
                    display: inline-block;
                    margin-right: 10px;
                    font-size: 1.2em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <div class="header-content">
                        <h1>🛡️ Aegis Vanguard</h1>
                        <p>Advanced Website Security Scanner</p>
                    </div>
                </header>
                
                <div class="info">
                    <p><span class="shield-icon">🔍</span> <strong>Scan Date:</strong> {{ scan_date }}</p>
                    <p><span class="shield-icon">📁</span> <strong>Website Folder:</strong> {{ website_folder }}</p>
                </div>
                
                <div class="summary">
                    <h2>🔐 Vulnerability Summary</h2>
                    
                    <div class="stats-grid">
                        <div class="stat-box">
                            <h3>Total Vulnerabilities</h3>
                            <div class="value">{{ total }}</div>
                        </div>
                        
                        <div class="stat-box">
                            <h3>Critical</h3>
                            <div class="value critical-stat">{{ critical }}</div>
                        </div>
                        
                        <div class="stat-box">
                            <h3>High</h3>
                            <div class="value high-stat">{{ high }}</div>
                        </div>
                        
                        <div class="stat-box">
                            <h3>Medium</h3>
                            <div class="value medium-stat">{{ medium }}</div>
                        </div>
                        
                        <div class="stat-box">
                            <h3>Low</h3>
                            <div class="value low-stat">{{ low }}</div>
                        </div>
                    </div>
                </div>
                
                <h2>⚠️ Detected Vulnerabilities</h2>
                
                {% if vulnerabilities %}
                    {% for vuln in vulnerabilities %}
                        <div class="vulnerability {{ vuln.severity }}">
                            <h3>{{ vuln.description }} ({{ vuln.severity|capitalize }})</h3>
                            <p><strong>File:</strong> <span class="code">{{ vuln.file_path }}</span> (Line: {{ vuln.line_number }})</p>
                            <div class="fix">
                                <strong>🔧 Recommended Fix:</strong><br>
                                {{ vuln.fix }}
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="vulnerability low">
                        <h3>No vulnerabilities detected</h3>
                        <p>Your website appears to be secure. Continue to monitor and follow security best practices.</p>
                    </div>
                {% endif %}
                
                <footer>
                    <p>Generated by Aegis Vanguard Security Scanner | RunIT CLI Tool</p>
                </footer>
            </div>
        </html>
        """

        template = jinja2.Template(template_str)
        
        total = len(vulnerabilities)
        critical = sum(1 for v in vulnerabilities if v.severity == "critical")
        high = sum(1 for v in vulnerabilities if v.severity == "high")
        medium = sum(1 for v in vulnerabilities if v.severity == "medium")
        low = sum(1 for v in vulnerabilities if v.severity == "low")
        
        html_content = template.render(
            scan_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            website_folder=website_folder,
            vulnerabilities=[
                {
                    "description": v.description,
                    "severity": v.severity,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "fix": v.fix
                } for v in vulnerabilities
            ],
            total=total,
            critical=critical,
            high=high,
            medium=medium,
            low=low
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _print_error(self, message: str) -> None:
        """Print error message with color if available."""
        if HAS_COLORAMA:
            print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
        else:
            print(f"❌ {message}")

    def _print_success(self, message: str) -> None:
        """Print success message with color if available."""
        if HAS_COLORAMA:
            print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            print(f"✓ {message}")

    def _get_severity_color(self, severity: str) -> str:
        """Get color code for severity level."""
        if not HAS_COLORAMA:
            return ""
            
        if severity == "critical":
            return Fore.RED
        elif severity == "high":
            return Fore.YELLOW
        elif severity == "medium":
            return Fore.YELLOW
        elif severity == "low":
            return Fore.GREEN
        return ""