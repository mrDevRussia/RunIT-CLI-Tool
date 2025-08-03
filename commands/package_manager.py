#!/usr/bin/env python3
"""
Package Manager for RunIT CLI Tool
Handles package installation, updates, and management.

Author: RunIT Development Team
Version: 1.2.0
License: MIT
"""

import os
import json
import shutil
import urllib.request
import urllib.error
import zipfile
import tempfile
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.logger import Logger
from utils.file_utils import FileUtils


class PackageManager:
    """
    Manages packages for the RunIT CLI tool.
    Handles installation, updates, version tracking, and package registry.
    """

    def __init__(self):
        """Initialize the Package Manager."""
        self.logger = Logger()
        self.file_utils = FileUtils()
        self.current_version = "1.2.0"
        
        # Package directories
        self.packages_dir = Path("packages")
        self.registry_file = Path("package_registry.json")
        self.config_file = Path("package_config.json")
        
        # Ensure directories exist
        self.packages_dir.mkdir(exist_ok=True)
        
        # Initialize registry if it doesn't exist
        if not self.registry_file.exists():
            self._init_registry()
        
        # Initialize config if it doesn't exist
        if not self.config_file.exists():
            self._init_config()
            
        # Load registry and config
        self.registry = self._load_registry()
        self.config = self._load_config()
        
    def _load_registry(self) -> dict:
        """Load the package registry."""
        with open(self.registry_file) as f:
            return json.load(f)
            
    def _load_config(self) -> dict:
        """Load the package configuration."""
        with open(self.config_file) as f:
            return json.load(f)
            
    def get_installed_packages(self) -> Dict[str, dict]:
        """Get all installed packages from the registry.
        
        Returns:
            Dict[str, dict]: Dictionary of installed packages and their information
        """
        return {name: info for name, info in self.registry["packages"].items()}

    def install_package(self, package_name: str) -> bool:
        """Install a package from its GitHub repository.
        
        Args:
            package_name: Name of the package to install
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            # Check if package exists in registry
            if package_name not in self.registry["packages"]:
                self.logger.error(f"Package {package_name} not found in registry")
                return False
                
            package_info = self.registry["packages"][package_name]
            repo_url = package_info["repository"]
            
            # Create package directory
            package_dir = self.packages_dir / package_name
            package_dir.mkdir(exist_ok=True)
            
            # Clone the repository
            try:
                subprocess.run(
                    ["git", "clone", repo_url, str(package_dir)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to clone repository: {e.stderr}")
                return False
                
            # Verify package configuration
            package_config = package_dir / "package_info.json"
            if not package_config.exists():
                self.logger.error(f"Package {package_name} is missing package_info.json")
                shutil.rmtree(package_dir)
                return False
                
            # Load and validate package configuration
            with open(package_config) as f:
                config = json.load(f)
                
            required_fields = ["name", "version", "main_file", "dependencies"]
            if not all(field in config for field in required_fields):
                self.logger.error(f"Package {package_name} has invalid package_info.json")
                shutil.rmtree(package_dir)
                return False
                
            # Update registry
            self.registry["packages"][package_name]["installed"] = True
            self.registry["packages"][package_name]["install_path"] = str(package_dir)
            self.registry["packages"][package_name]["version"] = config["version"]
            
            with open(self.registry_file, "w") as f:
                json.dump(self.registry, f, indent=2)
                
            # Update config
            self.config["installed_packages"].append(package_name)
            self.config["package_paths"][package_name] = str(package_dir)
            
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
                
            self.logger.info(f"Successfully installed package {package_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install package {package_name}: {str(e)}")
            return False

    def _init_registry(self):
        """Initialize the package registry with built-in packages."""
        registry = {
            "packages": {
                "preview_RunIT": {
                    "name": "preview_RunIT",
                    "version": "1.0.0",
                    "description": "Preview HTML files in the browser",
                    "repository": "https://github.com/runit-packages/preview-runit",
                    "main_file": "preview.py",
                    "dependencies": [],
                    "installed": False,
                    "install_path": None
                },

                "Edit_RunIT": {
                    "name": "Edit_RunIT",
                    "version": "1.0.0",
                    "description": "Advanced file editing capabilities",
                    "repository": "https://github.com/runit-packages/edit-runit",
                    "main_file": "editor.py",
                    "dependencies": [],
                    "installed": False,
                    "install_path": None
                }
            

            },
            "core_tool": {
                "name": "RunIT",
                "version": self.current_version,
                "last_updated": None
            }
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        self.logger.info("Package registry initialized")

    def _init_config(self):
        """Initialize package configuration."""
        config = {
            "auto_update": False,
            "registry_url": "https://github.com/runit-packages/registry",
            "installed_packages": [],
            "package_paths": {},
            "github_token": None  # Optional: For private repositories
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("Package configuration initialized")

    def _load_registry(self) -> Dict:
        """Load the package registry."""
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load registry: {e}")
            return {"packages": {}, "core_tool": {}}

    def _save_registry(self, registry: Dict):
        """Save the package registry."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")

    def _load_config(self) -> Dict:
        """Load package configuration."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

    def _save_config(self, config: Dict):
        """Save package configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def install_package(self, package_name: str) -> bool:
        """
        Install a package from GitHub releases.
        
        Args:
            package_name (str): Name of the package to install (e.g., 'zen-mode_RunIT@latest')
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        try:
            # Parse package name and version
            if '@' not in package_name:
                print("❌ Invalid package format. Use: package_name@version (e.g., zen-mode_RunIT@latest)")
                return False
                
            name, version = package_name.split('@')
            
            # Get GitHub release
            github_url = f"https://api.github.com/repos/runit-packages/{name}/releases"
            
            try:
                with urllib.request.urlopen(github_url) as response:
                    releases = json.loads(response.read())
            except urllib.error.URLError as e:
                print(f"❌ Failed to fetch releases: {e}")
                return False
                
            if not releases:
                print(f"❌ No releases found for package {name}")
                return False
                
            # Get latest or specific version
            release = releases[0] if version == 'latest' else next(
                (r for r in releases if r['tag_name'] == version),
                None
            )
            
            if not release:
                print(f"❌ Version {version} not found for package {name}")
                return False
                
            # Download release assets
            assets_url = release['assets_url']
            try:
                with urllib.request.urlopen(assets_url) as response:
                    assets = json.loads(response.read())
            except urllib.error.URLError as e:
                print(f"❌ Failed to fetch release assets: {e}")
                return False
                
            if not assets:
                print(f"❌ No assets found in release {version}")
                return False
                
            # Create package directory
            package_dir = self.packages_dir / name
            package_dir.mkdir(exist_ok=True)
            
            # Download and extract package
            for asset in assets:
                if asset['name'].endswith('.zip'):
                    try:
                        # Download zip file
                        with urllib.request.urlopen(asset['browser_download_url']) as response:
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                shutil.copyfileobj(response, tmp_file)
                                
                        # Extract zip file
                        with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                            zip_ref.extractall(package_dir)
                            
                        # Cleanup
                        os.unlink(tmp_file.name)
                        
                        # Verify package structure
                        if not (package_dir / 'package_info.json').exists():
                            print("❌ Invalid package: missing package_info.json")
                            shutil.rmtree(package_dir)
                            return False
                            
                        # Update registry
                        registry = self._load_registry()
                        if name not in registry['packages']:
                            registry['packages'][name] = {
                                'name': name,
                                'version': release['tag_name'],
                                'description': release['body'] or 'No description available',
                                'repository': f"https://github.com/runit-packages/{name}",
                                'installed': True,
                                'install_path': str(package_dir)
                            }
                        else:
                            registry['packages'][name].update({
                                'version': release['tag_name'],
                                'installed': True,
                                'install_path': str(package_dir)
                            })
                        self._save_registry(registry)
                        
                        # Update config
                        config = self._load_config()
                        if name not in config['installed_packages']:
                            config['installed_packages'].append(name)
                        config['package_paths'][name] = str(package_dir)
                        self._save_config(config)
                        
                        print(f"✅ Successfully installed {name} version {release['tag_name']}")
                        return True
                        
                    except Exception as e:
                        print(f"❌ Failed to install package: {e}")
                        if package_dir.exists():
                            shutil.rmtree(package_dir)
                        return False
                        
            print("❌ No valid package archive found in release")
            return False
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            self.logger.error(f"Package installation failed: {e}")
            return False

    def _install_package_files(self, package_name: str, package_info: Dict, package_dir: Path) -> bool:
        """Install package files based on package type."""
        try:
            if "preview_RunIT" in package_name:
                return self._install_preview_package(package_dir)
            elif "Edit_RunIT" in package_name:
                return self._install_edit_package(package_dir)
            else:
                print(f"❌ Unknown package type: {package_name}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to install package files: {e}")
            return False

    def _install_preview_package(self, package_dir: Path) -> bool:
        """Install the preview package files."""
        try:
            # Create preview.py
            preview_code = '''#!/usr/bin/env python3
"""
Preview RunIT Package - HTML File Browser Preview
Allows users to preview HTML files in their default browser.
"""

import os
import webbrowser
from pathlib import Path
import tempfile
import shutil


class HTMLPreviewer:
    """HTML file previewer."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "RunIT_Preview"
        self.temp_dir.mkdir(exist_ok=True)
    
    def preview_file(self, filepath: str):
        """Preview an HTML file in the browser."""
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                print(f"❌ File not found: {filepath}")
                return False
            
            if file_path.suffix.lower() not in ['.html', '.htm']:
                print(f"❌ Not an HTML file: {filepath}")
                return False
            
            # Copy file to temp directory to avoid file locking issues
            temp_file = self.temp_dir / file_path.name
            shutil.copy2(file_path, temp_file)
            
            # Open in browser
            file_url = f"file://{temp_file.absolute()}"
            webbrowser.open(file_url)
            
            print(f"🌐 Opening {file_path.name} in your default browser...")
            return True
            
        except Exception as e:
            print(f"❌ Preview failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass


def main(args):
    """Main entry point for preview package."""
    if not args:
        print("❌ Please specify an HTML file to preview")
        print("Usage: preview <filename.html>")
        return
    
    previewer = HTMLPreviewer()
    previewer.preview_file(args[0])
'''
            
            with open(package_dir / "preview.py", 'w') as f:
                f.write(preview_code)
            
            # Create package info file
            info = {
                "name": "preview_RunIT",
                "version": "1.0.0",
                "description": "Preview HTML files in browser",
                "commands": ["preview"]
            }	
            with open(package_dir / "package_info.json", 'w') as f:
                json.dump(info, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install preview package: {e}")
            return False

    def _install_edit_package(self, package_dir: Path) -> bool:
        """Install the edit package files."""
        try:
            # Create editor.py
            editor_code = '''#!/usr/bin/env python3
"""
Edit RunIT Package - Advanced File Editor
Provides advanced file editing capabilities.
"""

import os
import subprocess
import sys
from pathlib import Path


class FileEditor:
    """Advanced file editor."""
    
    def __init__(self):
        self.editors = {
            'notepad': 'notepad.exe',
            'nano': 'nano',
            'vim': 'vim',
            'code': 'code',
            'notepad++': 'notepad++.exe'
        }
    
    def edit_file(self, filepath: str, editor: str = None):
        """Edit a file with specified or default editor."""
        try:
            file_path = Path(filepath)
            
            # Create file if it doesn't exist
            if not file_path.exists():
                print(f"📝 Creating new file: {filepath}")
                file_path.touch()
            
            # Determine editor to use
            editor_cmd = self._get_editor(editor)
            if not editor_cmd:
                print("❌ No suitable editor found")
                return False
            
            print(f"📝 Opening {filepath} with {editor_cmd}...")
            
            # Launch editor
            if os.name == 'nt':  # Windows
                subprocess.run([editor_cmd, str(file_path)])
            else:
                subprocess.run([editor_cmd, str(file_path)])
            
            return True
            
        except Exception as e:
            print(f"❌ Edit failed: {e}")
            return False
    
    def _get_editor(self, preferred_editor: str = None) -> str:
        """Get available editor command."""
        if preferred_editor and preferred_editor in self.editors:
            return self.editors[preferred_editor]
        
        # Try to find available editor
        for name, cmd in self.editors.items():
            if self._is_command_available(cmd):
                return cmd
        
        return None
    
    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available in the system."""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            try:
                subprocess.run(['where', command] if os.name == 'nt' else ['which', command],
                             capture_output=True, check=True)
                return True
            except:
                return False


def main(args):
    """Main entry point for edit package."""
    if not args:
        print("❌ Please specify a file to edit")
        print("Usage: edit <filename> [editor]")
        return
    
    editor_name = args[1] if len(args) > 1 else None
    editor = FileEditor()
    editor.edit_file(args[0], editor_name)
'''
            
            with open(package_dir / "editor.py", 'w') as f:
                f.write(editor_code)
            
            # Create package info file
            info = {
                "name": "Edit_RunIT",
                "version": "1.0.0",
                "description": "Advanced file editing capabilities",
                "commands": ["edit"]
            }
            
            with open(package_dir / "package_info.json", 'w') as f:
                json.dump(info, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install edit package: {e}")
            return False

    def update_package(self, package_name: str) -> bool:
        """
        Update a package or the core tool.
        
        Args:
            package_name (str): Name of package to update or 'RunIT@latest' for core tool
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if package_name == "RunIT@latest":
            return self._update_core_tool()
        
        registry = self._load_registry()
        
        if package_name not in registry["packages"]:
            print(f"❌ Package '{package_name}' not found")
            return False
        
        package_info = registry["packages"][package_name]
        
        if not package_info["installed"]:
            print(f"❌ Package '{package_name}' is not installed")
            print("   Use 'install' command to install it first")
            return False
        
        print(f"🔄 Updating package: {package_name}")
        
        # For now, reinstall the package (in real implementation, check for newer versions)
        package_dir = Path(package_info["install_path"])
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        # Reinstall
        package_info["installed"] = False
        self._save_registry(registry)
        
        return self.install_package(package_name)

    def _update_core_tool(self) -> bool:
        """Update the core RunIT tool from GitHub."""
        print("🔄 Checking for RunIT updates...")
        print(f"   Current version: {self.current_version}")
        
        # Check internet connectivity
        if not self._check_internet_connection():
            print("❌ No internet connection. Update requires internet connectivity.")
            print("   Please check your connection and try again.")
            return False
        
        config = self._load_config()
        github_info = config.get("github_repo", {})
        
        if not github_info:
            print("❌ GitHub repository not configured")
            return False
        
        try:
            # Check for updates on GitHub
            latest_version, has_update = self._check_github_updates(github_info)
            
            if not has_update:
                print("✅ RunIT is up to date!")
                registry = self._load_registry()
                registry["core_tool"]["last_updated"] = self._get_current_timestamp()
                self._save_registry(registry)
                return True
            
            print(f"🎉 New version available: {latest_version}")
            print("🔄 Downloading update from GitHub...")
            
            # Download and apply update
            if self._download_github_update(github_info, latest_version):
                print("✅ RunIT updated successfully!")
                print(f"   Updated from v{self.current_version} to v{latest_version}")
                print("   Please restart RunIT to use the new version.")
                
                # Update registry
                registry = self._load_registry()
                registry["core_tool"]["version"] = latest_version
                registry["core_tool"]["last_updated"] = self._get_current_timestamp()
                self._save_registry(registry)
                return True
            else:
                print("❌ Update failed. Please try again or download manually.")
                return False
                
        except Exception as e:
            print(f"❌ Update failed: {e}")
            self.logger.error(f"GitHub update failed: {e}")
            return False

    def _check_internet_connection(self) -> bool:
        """Check if internet connection is available."""
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except OSError:
            try:
                # Fallback: try GitHub
                socket.create_connection(("github.com", 443), timeout=5)
                return True
            except OSError:
                return False

    def _check_github_updates(self, github_info: Dict) -> Tuple[str, bool]:
        """Check for updates on GitHub."""
        try:
            owner = github_info["owner"]
            repo = github_info["repo"]
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            
            print(f"   Checking GitHub repository: {owner}/{repo}")
            
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                latest_version = data["tag_name"].lstrip("v")
                current_version = self.current_version
                
                # Simple version comparison (assumes semantic versioning)
                has_update = self._compare_versions(latest_version, current_version)
                
                return latest_version, has_update
                
        except urllib.error.URLError as e:
            print(f"   Network error: {e}")
            return self.current_version, False
        except Exception as e:
            print(f"   Error checking updates: {e}")
            return self.current_version, False

    def _compare_versions(self, latest: str, current: str) -> bool:
        """Compare version strings."""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
            
            return latest_parts > current_parts
        except Exception:
            return latest != current

    def _download_github_update(self, github_info: Dict, version: str) -> bool:
        """Download and apply GitHub update."""
        try:
            owner = github_info["owner"]
            repo = github_info["repo"]
            branch = github_info.get("branch", "main")
            
            download_url = f"https://github.com/{owner}/{repo}/archive/{branch}.zip"
            
            print(f"   Downloading from: {download_url}")
            
            # Create backup if enabled
            config = self._load_config()
            if config.get("update_settings", {}).get("backup_before_update", True):
                self._create_backup()
            
            # Download to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_file = temp_path / "update.zip"
                
                # Download the zip file
                urllib.request.urlretrieve(download_url, zip_file)
                
                # Extract the zip file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find the extracted directory
                extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir()]
                if not extracted_dirs:
                    print("❌ No extracted directory found")
                    return False
                
                update_dir = extracted_dirs[0]
                
                # Apply update (copy new files)
                return self._apply_update(update_dir)
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
            self.logger.error(f"GitHub download failed: {e}")
            return False

    def _create_backup(self) -> bool:
        """Create a backup of the current installation."""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = self._get_current_timestamp().replace(":", "-").replace(" ", "_")
            backup_path = backup_dir / f"RunIT_backup_{timestamp}"
            
            print(f"   Creating backup: {backup_path}")
            
            # Copy important files
            files_to_backup = [
                "main.py",
                "commands/",
                "utils/",
                "docs/",
                "package_registry.json",
                "package_config.json"
            ]
            
            backup_path.mkdir(exist_ok=True)
            
            for item in files_to_backup:
                src = Path(item)
                if src.exists():
                    dst = backup_path / item
                    if src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
            
            print(f"   Backup created successfully")
            return True
            
        except Exception as e:
            print(f"   Backup failed: {e}")
            return False

    def _apply_update(self, update_dir: Path) -> bool:
        """Apply the downloaded update."""
        try:
            print("   Applying update...")
            
            # Files to update
            update_files = [
                "main.py",
                "commands/",
                "docs/",
                "package_registry.json",
                "package_config.json",
                "utils/"
            ]
            
            for item in update_files:
                src = update_dir / item
                dst = Path(item)
                
                if src.exists():
                    if src.is_dir():
                        # Update directory
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        # Update file
                        shutil.copy2(src, dst)
                    
                    print(f"   Updated: {item}")
            
            print("   Update applied successfully")
            return True
            
        except Exception as e:
            print(f"   Failed to apply update: {e}")
            return False

    def _get_current_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def list_packages(self):
        """List all available and installed packages."""
        registry = self._load_registry()
        
        print("\n📦 RunIT Package Registry")
        print("="*50)
        
        print(f"\n🔧 Core Tool:")
        core = registry["core_tool"]
        print(f"   RunIT v{core['version']}")
        if core.get("last_updated"):
            print(f"   Last updated: {core['last_updated']}")
        
        print(f"\n📚 Available Packages:")
        for pkg_name, pkg_info in registry["packages"].items():
            status = "✅ Installed" if pkg_info["installed"] else "⚪ Available"
            print(f"   {pkg_name:<25} - {pkg_info['description']}")
            print(f"   {' '*27} Version: {pkg_info['version']} | {status}")
        
        print(f"\n💡 Use 'install <package_name@latest>' to install a package")
        print(f"💡 Use 'update <package_name@latest>' to update a package")

    def get_version(self) -> str:
        """Get the current RunIT version."""
        return self.current_version

    def test_installation(self) -> bool:
        """Test the package system installation."""
        try:
            print("🧪 Testing Package System...")
            print("="*40)
            
            # Test registry loading
            registry = self._load_registry()
            print("✅ Registry loaded successfully")
            
            # Test config loading
            config = self._load_config()
            print("✅ Configuration loaded successfully")
            
            # Test package directory
            if self.packages_dir.exists():
                print("✅ Package directory exists")
            else:
                print("❌ Package directory missing")
                return False
            
            # Test available packages
            available_packages = len(registry["packages"])
            print(f"✅ {available_packages} packages available in registry")
            
            # Test installed packages
            installed_packages = len([p for p in registry["packages"].values() if p["installed"]])
            print(f"📦 {installed_packages} packages currently installed")
            
            print("✅ Package system test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Package system test failed: {e}")
            self.logger.error(f"Package system test failed: {e}")
            return False