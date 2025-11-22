import os
import json
import base64
import uuid
import time
import socket
import platform
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import requests


DATA_DIR = Path('data')
CLIENT_ID_PATH = DATA_DIR / 'client_id.json'
ALLOWED_PATH = DATA_DIR / 'allowed_clients.json'


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def get_or_create_client_id() -> str:
    ensure_data_dir()
    if CLIENT_ID_PATH.exists():
        try:
            with open(CLIENT_ID_PATH, 'r', encoding='utf-8') as f:
                obj = json.load(f)
                cid = obj.get('client_id')
                if isinstance(cid, str) and cid:
                    return cid
        except Exception:
            pass
    return ''


def has_client_id() -> bool:
    ensure_data_dir()
    if CLIENT_ID_PATH.exists():
        try:
            with open(CLIENT_ID_PATH, 'r', encoding='utf-8') as f:
                obj = json.load(f)
                cid = obj.get('client_id')
                return isinstance(cid, str) and bool(cid)
        except Exception:
            return False
    return False


def load_allowed_clients() -> list:
    ensure_data_dir()
    if ALLOWED_PATH.exists():
        try:
            with open(ALLOWED_PATH, 'r', encoding='utf-8') as f:
                obj = json.load(f)
                items = obj.get('allowed_clients')
                if isinstance(items, list):
                    return [str(x) for x in items]
        except Exception:
            pass
    return []


def save_allowed_clients(items: list):
    ensure_data_dir()
    try:
        with open(ALLOWED_PATH, 'w', encoding='utf-8') as f:
            json.dump({'allowed_clients': list(items)}, f, indent=2)
    except Exception:
        pass


class Fail2Ban:
    def __init__(self, threshold: int = 3, ban_seconds: int = 60):
        self.threshold = threshold
        self.ban_seconds = ban_seconds
        self.store = {}

    def record_failure(self, ip: str):
        now = time.time()
        item = self.store.get(ip)
        if item and item.get('banned_until', 0) > now:
            return
        count = (item.get('count', 0) + 1) if item else 1
        banned_until = item.get('banned_until', 0) if item else 0
        if count >= self.threshold:
            banned_until = now + self.ban_seconds
            count = 0
        self.store[ip] = {'count': count, 'banned_until': banned_until}

    def is_banned(self, ip: str) -> bool:
        now = time.time()
        item = self.store.get(ip)
        if not item:
            return False
        return item.get('banned_until', 0) > now

    def reset(self, ip: str):
        self.store.pop(ip, None)


class PortGuardian:
    def __init__(self, stealth: bool = False):
        self.authorized_ip = None
        self.locked = False
        self.stealth = stealth

    def lock_to(self, ip: str):
        self.authorized_ip = ip
        self.locked = True

    def accepts(self, ip: str) -> bool:
        if not self.locked:
            return not self.stealth
        return ip == self.authorized_ip


def encrypt_aes_gcm(key: bytes, plaintext: str):
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ct = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
    tag = encryptor.tag
    return nonce, ct, tag


def decrypt_aes_gcm(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> str:
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    pt = decryptor.update(ciphertext) + decryptor.finalize()
    return pt.decode('utf-8', errors='ignore')


def b64(x: bytes) -> str:
    return base64.b64encode(x).decode('utf-8')


def b64d(s: str) -> bytes:
    return base64.b64decode(s)


def _detect_public_ip() -> str:
    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=5)
        if r.status_code == 200:
            return r.json().get('ip', '')
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return ''


def _device_fingerprint() -> str:
    ip = _detect_public_ip()
    host = socket.gethostname()
    mac = uuid.getnode()
    osinfo = platform.platform()
    py = platform.python_version()
    return f"{host}|{mac}|{osinfo}|{ip}|{py}"


def generate_device_client_id() -> str:
    ensure_data_dir()
    if CLIENT_ID_PATH.exists():
        try:
            with open(CLIENT_ID_PATH, 'r', encoding='utf-8') as f:
                obj = json.load(f)
                cid = obj.get('client_id')
                if isinstance(cid, str) and cid:
                    return cid
        except Exception:
            pass
    fp = _device_fingerprint().encode('utf-8')
    digest = hashlib.sha256(fp).digest()
    cid = str(uuid.uuid5(uuid.NAMESPACE_DNS, base64.b64encode(digest).decode('utf-8')))
    try:
        with open(CLIENT_ID_PATH, 'w', encoding='utf-8') as f:
            json.dump({'client_id': cid}, f)
    except Exception:
        pass
    return cid