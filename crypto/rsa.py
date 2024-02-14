from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from typing import Tuple


def generate_key_pair() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    return private_key, public_key


def encrypt_message(public_key: rsa.RSAPublicKey, message: bytes) -> bytes:
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


def decrypt_message(private_key: rsa.RSAPrivateKey, ciphertext: bytes) -> bytes:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plaintext


def public_key_to_bytes(public_key: rsa.RSAPublicKey):
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_bytes


def bytes_to_public_key(public_key_bytes: bytes) -> rsa.RSAPublicKey:
    public_key = serialization.load_pem_public_key(
        public_key_bytes, backend=default_backend()
    )

    if isinstance(public_key, rsa.RSAPublicKey):
        return public_key

    raise RuntimeError("invalid key type, expecting RSAPublicKey")
