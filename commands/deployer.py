"""Deployer Module for RunIT CLI Tool.
Handles local hosting and deployment of static websites.
"""

import http.server
import socketserver
import os
import socket
import webbrowser
import functools
import logging
from pathlib import Path

class Deployer:
    """Handles local hosting and deployment of static websites."""

    def __init__(self):
        """Initialize the Deployer with default settings."""
        self.PORT = 8000  # Default port
        self.server = None
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_port(self, port: int):
        """Change the port number for deployment"""
        if isinstance(port, int) and 1024 <= port <= 65535:
            self.PORT = port
            print(f"✅ Port changed to {port}")
            return True
        print("❌ Invalid port number. Please use a number between 1024 and 65535")
        return False

    def _run_server(self):
        """Internal method to run the server with error handling"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"\n❌ Server error: {str(e)}")
            self.stop_deployment()

    def stop_deployment(self):
        """Stop any running deployment servers and tunnels"""
        try:
            # First try to stop our own server instance
            if self.server:
                try:
                    self.logger.info("Stopping local server...")
                    self.server.shutdown()
                    self.server.server_close()
                    self.server = None
                    self.logger.info("Local server stopped successfully")
                    print("✅ Local server stopped successfully")
                except Exception as e:
                    self.logger.error(f"Failed to stop local server: {e}")
                    pass

            import subprocess
            import time
            import socket

            # Kill all Python processes (they might be holding the port)
            try:
                self.logger.info("Terminating Python processes...")
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
                print("✅ Terminated Python processes")
                time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Failed to terminate Python processes: {e}")
                pass

            # Simple port check
            def is_port_free():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.bind(("127.0.0.1", self.PORT))
                    sock.close()
                    return True
                except:
                    return False

            if is_port_free():
                self.logger.info(f"Port {self.PORT} is now free")
                print(f"✅ Port {self.PORT} is now free")
            else:
                self.logger.warning(f"Port {self.PORT} is still in use")
                print(f"❌ Port {self.PORT} is still in use")
                print("Please close any applications using this port or restart your computer")
                return False

            # Close the localtunnel process if it exists
            if hasattr(self, 'tunnel_process') and self.tunnel_process:
                self.logger.info("Closing localtunnel connection...")
                try:
                    self.tunnel_process.terminate()
                    self.tunnel_process.wait(timeout=5)
                    self.tunnel_process = None
                    print("✅ Tunnel connection closed")
                except Exception as e:
                    self.logger.error(f"Error closing tunnel: {e}")
                    print(f"❌ Error closing tunnel: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Error stopping deployment: {e}")
            print(f"❌ Error stopping deployment: {str(e)}")
            return False

    def deploy_site(self, site_folder: str):
        """Deploy a static website from the specified folder"""
        # Validate folder path
        if not os.path.exists(site_folder):
            self.logger.error(f"Folder not found: {site_folder}")
            print(f"❌ Folder not found: {site_folder}")
            return False

        # Check if port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", self.PORT))
            sock.close()
        except socket.error:
            self.logger.error(f"Port {self.PORT} is already in use")
            print(f"❌ Port {self.PORT} is already in use")
            print("Please try:")
            print("1. Run 'stopdeploy' to stop any running servers")
            print("2. Use 'setport <number>' to try a different port")
            return False

        # Store original directory
        original_dir = os.getcwd()
        
        try:
            # Convert relative path to absolute path
            abs_site_folder = os.path.abspath(site_folder)
            # Change to the specified directory
            os.chdir(abs_site_folder)
            self.logger.info(f"Changed directory to: {abs_site_folder}")
            
            # Create and configure the server with custom handler
            handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=abs_site_folder)
            self.server = socketserver.TCPServer(("localhost", self.PORT), handler)
            self.server.allow_reuse_address = True
            
            # Start the server in a daemon thread
            import threading
            server_thread = threading.Thread(target=self._run_server)
            server_thread.daemon = True
            server_thread.start()
            self.logger.info("Server thread started")
            
            # Wait a moment to ensure server starts
            import time
            time.sleep(1)
            
            # Verify server is running
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.connect(("localhost", self.PORT))
                test_socket.close()
                
                server_url = f"http://localhost:{self.PORT}"
                self.logger.info(f"Local server started successfully at: {server_url}")
                print(f"✨ Local server started at: {server_url}")
                print(f"📂 Serving files from: {abs_site_folder}")
                print("")
                print("ℹ️  Server is running in the background")
                print("💡 Use 'stopdeploy' command to stop the server")
                print("-" * 50)
                
                # Open the site in default browser
                webbrowser.open(server_url)
                self.logger.info("Opened server URL in default browser")
                
                # Return to original directory
                os.chdir(original_dir)
                return True
                
            except socket.error:
                self.logger.error("Failed to verify server is running")
                print("❌ Failed to start server")
                self.stop_deployment()
                os.chdir(original_dir)
                return False
            
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
            print(f"\n❌ Server error: {str(e)}")
            self.stop_deployment()
            os.chdir(original_dir)
            return False

    def share(self):
        """
        Generate a public URL using localtunnel.
        Requires internet connection and localtunnel package.
        """
        if not self.server:
            self.logger.error("No server is running. Please deploy a site first.")
            print("❌ Error: No server is running. Please deploy a site first using 'deploy <folder>'")
            return False

        try:
            import subprocess
            import random
            import string
            import json
            import time

            # Generate a random subdomain
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            subdomain = f"mysite-{random_id}"

            self.logger.info("Share feature is currently unavailable")
            print("⚠️  The share feature is currently not available.")
            print("ℹ️  You can still access your site locally at http://localhost:" + str(self.PORT))
            return False

            # Construct the public URL
            public_url = f"https://{subdomain}.loca.lt"
            self.logger.info(f"Tunnel established at: {public_url}")
            print(f"✨ Your site is now accessible at: {public_url}")
            print("")
            print("ℹ️  The tunnel will remain active until you stop the server")
            print("💡 Use 'stopdeploy' command to stop both the server and tunnel")
            print("-" * 50)

            return True

        except Exception as e:
            self.logger.error(f"Error creating tunnel: {str(e)}")
            print(f"❌ Error creating tunnel: {str(e)}")
            return False
            return
            
        try:
            print("🔄 Generating public URL...")
            
            # Try to use a free tunneling service that doesn't require installation
            # We'll use a simple approach with a few popular services
            
            # First, check internet connectivity
            if not self._check_internet_connection():
                print("❌ No internet connection detected")
                print("Please check your internet connection and try again")
                return
            
            # Use a Python-based tunneling implementation
            try:
                import threading
                import requests
                import websockets
                import asyncio
                from urllib.parse import urljoin
                
                # Generate a random subdomain
                subdomain = f"runit-{random.randint(1000, 9999)}"
                tunnel_host = "tunnel.us.ngrok.com"
                
                print(f"📡 Connecting to tunneling service...")
                print(f"⏳ This may take a few moments...")
                
                # Create tunnel connection
                async def create_tunnel():
                    uri = f"wss://{tunnel_host}/tunnel"
                    async with websockets.connect(uri) as websocket:
                        # Send initial handshake
                        await websocket.send(json.dumps({
                            "type": "tunnel",
                            "payload": {
                                "subdomain": subdomain,
                                "port": self.PORT
                            }
                        }))
                        
                        response = await websocket.recv()
                        data = json.loads(response)
                        
                        if data.get("type") == "url":
                            self.public_url = data["payload"]["url"]
                            print(f"\n🌐 Public URL: {self.public_url}")
                            print("This URL will be active as long as your local server is running")
                            
                            # Keep the tunnel alive
                            while True:
                                try:
                                    await websocket.ping()
                                    await asyncio.sleep(25)
                                except:
                                    break
                
                # Start tunnel in background
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                tunnel_thread = threading.Thread(target=lambda: loop.run_until_complete(create_tunnel()))
                tunnel_thread.daemon = True
                tunnel_thread.start()
                    
            except Exception as e:
                self.logger.error(f"Error with IP lookup: {e}")
                # Continue to alternative method
            
            # If we get here, we couldn't establish a tunnel
            print("\n⚠️ Could not generate a public URL")
            print("\nPlease ensure you have the required dependencies installed:")
            print("Run: pip install -r deps/dependencies.txt")
            print("\nThis could also be due to:")
            print("1. Network connectivity issues")
            print("2. Firewall blocking WebSocket connections")
            print("3. Service temporary unavailability")
            print("\nPlease try again after installing dependencies")
            print("If the issue persists, check your internet connection and firewall settings")
            
        except Exception as e:
            self.logger.error(f"Error generating public URL: {e}")
            print(f"❌ Error generating public URL: {e}")
            print("Please check your internet connection and try again")
    
    def _check_internet_connection(self):
        """Check if there is an active internet connection."""
        try:
            # Try to connect to a reliable host
            socket.create_connection(("www.google.com", 80), timeout=3)
            return True
        except OSError:
            try:
                # Try an alternative host
                socket.create_connection(("www.microsoft.com", 80), timeout=3)
                return True
            except OSError:
                return False