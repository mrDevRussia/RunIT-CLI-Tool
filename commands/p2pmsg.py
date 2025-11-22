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
from utils.logger import Logger
from commands.security import (
    get_or_create_client_id,
    load_allowed_clients,
    save_allowed_clients,
    Fail2Ban,
    PortGuardian,
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    b64,
    b64d,
)
from commands.dh_utils import (
    generate_keypair,
    load_public_key_b64,
    derive_shared_secret,
    derive_session_keys,
)
from commands.hmac_utils import compute_hmac, verify_hmac


class P2PMessenger:
    def __init__(self):
        self.logger = Logger()
        self.running = False
        self.punching = False
        self.peer_addr = None
        self.sock = None
        self.session_code = None
        self.session_token = None
        self.role = None  # 'host' or 'guest'
        # Local cache file (privacy-focused; no messages stored)
        self.data_dir = Path('data')
        self.cache_file = self.data_dir / 'p2p_sessions.json'
        self._ensure_cache()
        self.client_id = None
        self.fail2ban = Fail2Ban()
        self.guardian = PortGuardian(stealth=False)
        self.aes_key = None
        self.hmac_key = None
        self.priv_key = None

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

    def _encrypt_msg(self, plaintext: str) -> bytes:
        nonce, ct, tag = encrypt_aes_gcm(self.aes_key, plaintext)
        mac = compute_hmac(self.hmac_key, nonce + ct + tag)
        msg = f"MSG:{b64(nonce)}:{b64(ct)}:{b64(tag)}:{b64(mac)}".encode('utf-8')
        return msg

    def _decrypt_msg(self, text: str) -> str:
        parts = text.split(':')
        if len(parts) != 5:
            raise ValueError('invalid message format')
        n = b64d(parts[1])
        c = b64d(parts[2])
        t = b64d(parts[3])
        m = b64d(parts[4])
        if not verify_hmac(self.hmac_key, n + c + t, m):
            raise ValueError('invalid hmac')
        return decrypt_aes_gcm(self.aes_key, n, c, t)

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

            if text.startswith('HS1:'):
                ip = addr[0]
                if self.fail2ban.is_banned(ip):
                    continue
                parts = text.split(':', 4)
                if len(parts) != 5:
                    self.fail2ban.record_failure(ip)
                    continue
                cid = parts[1]
                tok = parts[2]
                guest_pub_b64 = parts[3]
                if self.role == 'host':
                    allowed = load_allowed_clients()
                    if cid not in allowed or tok != self.session_token:
                        self.fail2ban.record_failure(ip)
                        continue
                    self.guardian.lock_to(ip)
                    try:
                        guest_pub = load_public_key_b64(guest_pub_b64)
                        self.priv_key, host_pub_b64 = generate_keypair()
                        shared = derive_shared_secret(self.priv_key, guest_pub)
                        self.aes_key, self.hmac_key = derive_session_keys(shared)
                        self.sock.sendto(f"HS2:{host_pub_b64}".encode('utf-8'), addr)
                    except Exception as e:
                        self.logger.error(f"Handshake processing error: {e}")
                        self.fail2ban.record_failure(ip)
                    continue
                continue
            elif text.startswith('HS2:'):
                ip = addr[0]
                if self.role == 'guest':
                    try:
                        host_pub_b64 = text.split(':', 1)[1]
                        host_pub = load_public_key_b64(host_pub_b64)
                        shared = derive_shared_secret(self.priv_key, host_pub)
                        self.aes_key, self.hmac_key = derive_session_keys(shared)
                        self.guardian.lock_to(ip)
                        try:
                            self.sock.sendto(b'HS_ACK', addr)
                        except Exception:
                            pass
                        print("✅ Handshake acknowledged by host. Tunnel established.")
                    except Exception as e:
                        self.logger.error(f"Handshake finalize error: {e}")
                    continue
                continue
            elif text.startswith('HS_ACK'):
                print("✅ Guest acknowledged handshake. Tunnel established.")
                continue
            elif text.startswith('PUNCH'):
                continue
            elif text.startswith('MSG:'):
                ip = addr[0]
                if self.guardian.locked and ip != self.guardian.authorized_ip:
                    continue
                try:
                    msg = self._decrypt_msg(text)
                    print(f"Peer: {msg}")
                except Exception as e:
                    self.logger.error(f"Decryption failed: {e}")
                continue
            else:
                if self.guardian.locked:
                    continue
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
                msg = self._encrypt_msg(user_input)
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
        self.aes_key = None
        self.hmac_key = None
        self.priv_key = None

    def _generate_session_code(self) -> str:
        # 16-digit numeric code
        return ''.join(str(random.randint(0, 9)) for _ in range(16))

    def start(self, args=None):
        stealth = False
        if args:
            stealth = '--stealth' in args
        self.guardian = PortGuardian(stealth=stealth)
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
        self.session_token = hashlib.sha256(self.session_code.encode('utf-8')).hexdigest()

        print(f"Your session code: {self.session_code}")
        print("Share it with the other user.")
        print(f"Your public IP: {public_ip}")
        print(f"Listening port: {local_port}")
        print("Waiting for guest handshake packet...")
        allowed = load_allowed_clients()
        try:
            add = input("Add allowed client_id (optional): ").strip()
        except Exception:
            add = ''
        if add:
            if add not in allowed:
                allowed.append(add)
                save_allowed_clients(allowed)

        # Save cache
        self._save_cache({
            'role': 'host',
            'session_code': self.session_code,
            'public_ip': public_ip,
            'port': local_port
        })

        self.running = True
        self._start_loops()

        guest_addr = None
        handshake_deadline = time.time() + 120
        while self.running and time.time() < handshake_deadline:
            try:
                data, addr = self.sock.recvfrom(65535)
            except (socket.timeout, OSError):
                continue
            except Exception as e:
                self.logger.error(f"Handshake error: {e}")
                continue
            try:
                txt = data.decode('utf-8', errors='ignore')
            except Exception:
                txt = ''
            if not txt.startswith('HS1:'):
                continue
            ip = addr[0]
            if self.fail2ban.is_banned(ip):
                continue
            parts = txt.split(':', 4)
            if len(parts) != 5:
                self.fail2ban.record_failure(ip)
                continue
            cid = parts[1]
            tok = parts[2]
            guest_pub_b64 = parts[3]
            allowed = load_allowed_clients()
            if cid not in allowed or tok != self.session_token:
                self.fail2ban.record_failure(ip)
                continue
            try:
                guest_pub = load_public_key_b64(guest_pub_b64)
                self.priv_key, host_pub_b64 = generate_keypair()
                shared = derive_shared_secret(self.priv_key, guest_pub)
                self.aes_key, self.hmac_key = derive_session_keys(shared)
                self.guardian.lock_to(ip)
                self.peer_addr = addr
                self.sock.sendto(f"HS2:{host_pub_b64}".encode('utf-8'), addr)
                print("✅ Guest connected. Starting encrypted P2P chat.")
                guest_addr = addr
                break
            except Exception as e:
                self.logger.error(f"Handshake error: {e}")
                self.fail2ban.record_failure(ip)
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
        self.session_token = hashlib.sha256(self.session_code.encode('utf-8')).hexdigest()
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

        print("Sending handshake to host...")
        try:
            cid = get_or_create_client_id()
            if not cid:
                print("This will generate a persistent Client ID based on your device and network info.")
                agree = input("Do you agree? (y/n): ").strip().lower()
                if agree not in ['y', 'yes']:
                    print("❌ Generation cancelled.")
                    return
                from commands.security import generate_device_client_id
                cid = generate_device_client_id()
            self.client_id = cid
        except Exception as e:
            self.logger.error(f"Client ID error: {e}")
            print("❌ Could not prepare Client ID.")
            return
        try:
            self.priv_key, pub_b64 = generate_keypair()
        except Exception as e:
            self.logger.error(f"DH key generation error: {e}")
            return
        hs1 = f"HS1:{self.client_id}:{self.session_token}:{pub_b64}:{random.randint(100000,999999)}".encode('utf-8')
        acked = False
        deadline = time.time() + 60
        while self.running and time.time() < deadline:
            try:
                self.sock.sendto(hs1, self.peer_addr)
                try:
                    data, addr = self.sock.recvfrom(65535)
                except (socket.timeout, OSError):
                    time.sleep(1.0)
                    continue
                txt = data.decode('utf-8', errors='ignore')
                if txt.startswith('HS2:'):
                    try:
                        host_pub_b64 = txt.split(':', 1)[1]
                        host_pub = load_public_key_b64(host_pub_b64)
                        shared = derive_shared_secret(self.priv_key, host_pub)
                        self.aes_key, self.hmac_key = derive_session_keys(shared)
                        self.guardian.lock_to(addr[0])
                        self.peer_addr = addr
                        try:
                            self.sock.sendto(b'HS_ACK', addr)
                        except Exception:
                            pass
                        print("✅ Host accepted handshake. Starting encrypted P2P chat.")
                        acked = True
                        break
                    except Exception as e:
                        self.logger.error(f"Handshake finalize error: {e}")
                        continue
            except Exception:
                time.sleep(1.0)

        if not acked:
            print("⚠️ Handshake not acknowledged yet. Continuing punches; you may still send messages after establishment.")

        # Begin chat
        self._chat_loop()
        self._close()