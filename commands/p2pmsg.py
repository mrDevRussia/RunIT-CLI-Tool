"""
P2P Messaging Command for RunIT CLI Tool
Provides encrypted global P2P messaging with UDP NAT traversal and hole punching.

Usage:
  p2pmsg  # interactive mode; choose Host or Guest

Security:
  AES-256-CBC encryption; key derived from SHA-256(session_code)
  Per-message random IV; messages not stored (privacy by design)

Note:
  NAT traversal depends on network/NAT type; hole punching is best-effort.
"""

import os
import socket
import threading
import time
import base64
import hashlib
import json
import random
from pathlib import Path

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

from utils.logger import Logger


class P2PMessenger:
    def __init__(self):
        self.logger = Logger()
        self.running = False
        self.punching = False
        self.peer_addr = None
        self.sock = None
        self.session_code = None
        self.session_key = None
        self.role = None  # 'host' or 'guest'
        # Local cache file (privacy-focused; no messages stored)
        self.data_dir = Path('data')
        self.cache_file = self.data_dir / 'p2p_sessions.json'
        self._ensure_cache()

    def _ensure_cache(self):
        try:
            self.data_dir.mkdir(exist_ok=True)
            if not self.cache_file.exists():
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
        except Exception as e:
            self.logger.error(f"Failed to prepare cache: {e}")

    def _save_cache(self, payload: dict):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")

    def _clear_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")

    def _derive_key(self, code: str) -> bytes:
        # key = SHA256(session_code)
        digest = hashlib.sha256(code.encode('utf-8')).digest()
        return digest  # 32 bytes

    def _encrypt(self, plaintext: str) -> bytes:
        # AES-256-CBC with per-message IV and PKCS7 padding
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.session_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        payload = iv + ciphertext
        return payload

    def _decrypt(self, data: bytes) -> str:
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(self.session_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()
        return plaintext.decode('utf-8', errors='ignore')

    def _detect_public_ip(self) -> str:
        try:
            r = requests.get('https://api.ipify.org?format=json', timeout=5)
            if r.status_code == 200:
                return r.json().get('ip', '')
        except Exception as e:
            self.logger.warning(f"Public IP detection failed via service: {e}")
        # Fallback best-effort: local hostname resolution (may be private IP)
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return 'Unknown'

    def _recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
            except (OSError, socket.timeout):
                continue
            except Exception as e:
                self.logger.error(f"Receive error: {e}")
                continue

            # Update peer_addr when receiving any traffic
            if self.peer_addr is None:
                self.peer_addr = addr

            try:
                text = data.decode('utf-8', errors='ignore')
            except Exception:
                text = ''

            # Control frames
            if text.startswith('HANDSHAKE'):
                # Record peer and acknowledge
                self.peer_addr = addr
                try:
                    self.sock.sendto(b'HANDSHAKE_ACK', addr)
                except Exception:
                    pass
                print("✅ Handshake received. P2P tunnel established.")
                continue
            elif text.startswith('HANDSHAKE_ACK'):
                print("✅ Handshake acknowledged by peer. Tunnel established.")
                continue
            elif text.startswith('PUNCH'):
                # Keepalive; no output needed
                continue
            elif text.startswith('MSG:'):
                # Encrypted payload in base64
                b64 = text[4:]
                try:
                    payload = base64.b64decode(b64)
                    msg = self._decrypt(payload)
                    print(f"Peer: {msg}")
                except Exception as e:
                    self.logger.error(f"Decryption failed: {e}")
                continue
            else:
                # Unknown traffic; ignore silently
                continue

    def _punch_loop(self):
        # Periodic NAT hole punching keepalive packets
        while self.punching and self.running and self.peer_addr is not None:
            try:
                self.sock.sendto(b'PUNCH', self.peer_addr)
            except Exception:
                pass
            time.sleep(2.0)

    def _start_loops(self):
        # Receiving loop
        self.sock.settimeout(1.0)
        t_recv = threading.Thread(target=self._recv_loop, daemon=True)
        t_recv.start()
        # Punching loop
        t_punch = threading.Thread(target=self._punch_loop, daemon=True)
        self.punching = True
        t_punch.start()

    def _chat_loop(self):
        print("Type messages to send. Use /exit to terminate the session.")
        while self.running:
            try:
                user_input = input('> ').strip()
            except (EOFError, KeyboardInterrupt):
                user_input = '/exit'
            if user_input.lower() == '/exit':
                break
            if not user_input:
                continue
            # Encrypt and send
            try:
                payload = self._encrypt(user_input)
                b64 = base64.b64encode(payload).decode('utf-8')
                msg = f"MSG:{b64}".encode('utf-8')
                if self.peer_addr:
                    self.sock.sendto(msg, self.peer_addr)
                else:
                    print("⚠️ Peer not yet known. Waiting for handshake...")
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")

    def _close(self):
        self.running = False
        self.punching = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self._clear_cache()
        print("🔒 Session closed. Cache cleared.")

    def _generate_session_code(self) -> str:
        # 16-digit numeric code
        return ''.join(str(random.randint(0, 9)) for _ in range(16))

    def start(self):
        try:
            choice = input("Host or Guest? (h/g): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("Operation cancelled.")
            return

        if choice == 'h':
            self.role = 'host'
            self._start_host()
        elif choice == 'g':
            self.role = 'guest'
            self._start_guest()
        else:
            print("❌ Invalid choice. Please enter 'h' or 'g'.")

    def _start_host(self):
        # Prepare socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))  # random port
        local_port = self.sock.getsockname()[1]
        public_ip = self._detect_public_ip()

        # Generate session code and key
        self.session_code = self._generate_session_code()
        self.session_key = self._derive_key(self.session_code)

        print(f"Your session code: {self.session_code}")
        print("Share it with the other user.")
        print(f"Your public IP: {public_ip}")
        print(f"Listening port: {local_port}")
        print("Waiting for guest handshake packet...")

        # Save cache
        self._save_cache({
            'role': 'host',
            'session_code': self.session_code,
            'public_ip': public_ip,
            'port': local_port
        })

        self.running = True
        self._start_loops()

        # Wait for handshake
        guest_addr = None
        handshake_deadline = time.time() + 120
        while self.running and time.time() < handshake_deadline:
            try:
                data, addr = self.sock.recvfrom(65535)
                if data.decode('utf-8', errors='ignore').startswith('HANDSHAKE'):
                    guest_addr = addr
                    self.peer_addr = guest_addr
                    self.sock.sendto(b'HANDSHAKE_ACK', guest_addr)
                    print("✅ Guest connected. Starting encrypted P2P chat.")
                    break
            except (socket.timeout, OSError):
                continue
            except Exception as e:
                self.logger.error(f"Handshake error: {e}")
                continue

        if not guest_addr:
            print("⚠️ No handshake received within timeout. You can keep waiting or /exit.")

        # Begin punching and chat
        self._chat_loop()
        self._close()

    def _start_guest(self):
        try:
            code = input("Enter session code: ").strip()
            host_ip = input("Enter host public IP: ").strip()
            host_port_str = input("Enter host port: ").strip()
            host_port = int(host_port_str)
        except Exception:
            print("❌ Invalid input.")
            return

        if not code.isdigit() or len(code) != 16:
            print("❌ Session code must be 16 digits.")
            return

        self.session_code = code
        self.session_key = self._derive_key(self.session_code)
        self.role = 'guest'

        # Prepare socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))  # random local port
        self.peer_addr = (host_ip, host_port)

        # Save cache
        self._save_cache({
            'role': 'guest',
            'session_code': self.session_code,
            'host_ip': host_ip,
            'host_port': host_port
        })

        self.running = True
        self._start_loops()

        # Send handshake and wait for ack
        print("Sending handshake to host...")
        handshake_msg = f"HANDSHAKE:{random.randint(100000, 999999)}".encode('utf-8')
        acked = False
        deadline = time.time() + 60
        while self.running and time.time() < deadline:
            try:
                self.sock.sendto(handshake_msg, self.peer_addr)
                # Try to receive ack
                try:
                    data, addr = self.sock.recvfrom(65535)
                    if data.decode('utf-8', errors='ignore').startswith('HANDSHAKE_ACK'):
                        print("✅ Host accepted handshake. Starting encrypted P2P chat.")
                        self.peer_addr = addr
                        acked = True
                        break
                except (socket.timeout, OSError):
                    pass
            except Exception:
                pass
            time.sleep(1.0)

        if not acked:
            print("⚠️ Handshake not acknowledged yet. Continuing punches; you may still send messages after establishment.")

        # Begin chat
        self._chat_loop()
        self._close()