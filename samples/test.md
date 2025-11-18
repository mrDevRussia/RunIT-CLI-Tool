<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RunIT v1.1 Installation System Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            color: #FFD700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .feature-list {
            list-style: none;
            padding: 0;
        }
        .feature-list li {
            background: rgba(255,255,255,0.2);
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #FFD700;
        }
        .feature-list li:before {
            content: "✅ ";
            font-weight: bold;
            color: #90EE90;
        }
        .version-badge {
            background: #FFD700;
            color: #333;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        }
        .package-info {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        # 🚀 RunIT v1.2.0 Installation System
        <div class="version-badge">Version 1.2.0 - Installation System Complete</div>
        
        <div class="package-info">
            ## 📦 Version 1.2.0 Features
            <ul class="feature-list">
                - Package Installation System (install command)
                - Package Update Management (update command)
                - File Structure Display (show command)
                - Advanced File Editing (edit command)
                - Directory Navigation (go command)
                - Version & Package Status (version command)
                - System Testing (test command)
                - HTML Preview Functionality (preview command)
            </ul>
        </div>
        
        <div class="package-info">
            ## 📚 Available Packages
            <ul class="feature-list">
                - **preview_RunIT@latest** - Preview HTML files in browser
                - **Edit_RunIT@latest** - Advanced file editing capabilities
            </ul>
        </div>

        <div class="package-info">
            ## 🎯 Usage Examples
            <ul class="feature-list">
                - install preview_RunIT@latest
                - install Edit_RunIT@latest
                - update RunIT@latest
                - show main.py
                - edit config.txt
                - go /path/to/directory
                - version
                - preview samples/test.html
            </ul>
        </div>
        
        <!-- Vulnerable code for testing (line 69) -->
        <script>
            function searchUser() {
                var userId = document.getElementById('userId').value;
                // SQL Injection vulnerability
                execute("SELECT * FROM users WHERE id = '" + userId + "'");
            }
        </script>
        
        <!-- Another vulnerable code for testing (line 92) -->
        <script>
            function updateProfile() {
                var name = document.getElementById('name').value;
                // SQL Injection vulnerability
                query("UPDATE users SET name = '" + name + "' WHERE id = 1");
            }
        </script>

        <p style="text-align: center; margin-top: 30px;">
            **RunIT v1.2.0 - Smart Terminal Assistant for Windows**<br>
            Installation System Successfully Implemented!
        </p>
    </div>
</body>
</html>