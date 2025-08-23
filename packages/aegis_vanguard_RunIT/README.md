# 🛡️ Aegis Vanguard (AV) - Website Security Scanner

Aegis Vanguard is a powerful security scanning tool for websites that detects vulnerabilities in your web application code and provides actionable fix suggestions.

## 📌 Installation

Install the package using RunIT's package manager:

```
install aegis_vanguard_RunIT@latest
```

## 📋 Features

- **Comprehensive Scanning**: Analyzes HTML, JS, PHP, and configuration files for security issues
- **Multiple Vulnerability Detection**: Identifies SQL Injection, XSS, File Inclusion, Weak Authentication, and more
- **Risk Assessment**: Assigns severity levels (Critical, High, Medium, Low) to each vulnerability
- **Detailed Reporting**: Generates reports in multiple formats (JSON, PDF, HTML)
- **Fix Suggestions**: Provides practical remediation advice for each detected vulnerability

## 🛠️ Usage

```
av <website_folder>
```

Where `<website_folder>` is the local directory containing your website files.

### Example

```
av my_website/
```

## 📊 Example Output

```
[+] Scanning website: my_website/
-----------------------------------
[!] SQL Injection detected in: login.php (Severity: High)
    ➤ Fix: Use Prepared Statements or ORM

[!] XSS vulnerability found in: search.html (Severity: Medium)
    ➤ Fix: Sanitize user inputs + Encode HTML output

[✓] SSL/TLS configuration is secure

-----------------------------------
⚠️ Full report saved at: reports/2025-08-22_report.pdf
```

## 🔍 Vulnerability Types

Aegis Vanguard detects the following types of vulnerabilities:

1. **SQL Injection**
   - Detects unsafe database queries that could allow attackers to manipulate your database
   - Severity: High
   - Fix: Use prepared statements or ORM instead of raw queries

2. **Cross-Site Scripting (XSS)**
   - Identifies code that allows unfiltered user input to be injected into HTML
   - Severity: Medium
   - Fix: Sanitize user inputs and encode HTML output

3. **File Inclusion (LFI/RFI)**
   - Detects code that could allow attackers to include unauthorized files
   - Severity: Critical
   - Fix: Validate file paths and use whitelisting

4. **Weak Authentication**
   - Finds hardcoded passwords, weak hashing algorithms, and other authentication issues
   - Severity: High
   - Fix: Use strong password hashing (bcrypt/Argon2) and enforce password policies

5. **Misconfigurations**
   - Identifies debug mode enabled in production, sensitive paths exposed, etc.
   - Severity: Low
   - Fix: Disable debug mode in production environments

## 📝 Report Formats

Aegis Vanguard generates reports in multiple formats:

- **JSON**: Machine-readable format for developers and integration with other tools
- **PDF**: Professional report format for companies and managers
- **HTML**: Interactive report that can be viewed in any browser

## 🔧 Dependencies

- colorama: For colored terminal output
- reportlab: For PDF report generation
- jinja2: For HTML report generation

## 📄 License

MIT License

## 👥 Author

RunIT Team