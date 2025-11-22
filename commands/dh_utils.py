import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519


def generate_keypair():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private_key, base64.b64encode(public_bytes).decode('utf-8')


def load_public_key_b64(b64_str):
    public_bytes = base64.b64decode(b64_str)
    return x25519.X25519PublicKey.from_public_bytes(public_bytes)


def derive_shared_secret(private_key, peer_public_key):
    return private_key.exchange(peer_public_key)


def derive_session_keys(shared_secret: bytes):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,
        salt=None,
        info=b"runit-p2p-session",
    )
    material = hkdf.derive(shared_secret)
    aes_key = material[:32]
    hmac_key = material[32:64]
    return aes_key, hmac_key