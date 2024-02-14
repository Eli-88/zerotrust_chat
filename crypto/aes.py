from cryptography.fernet import Fernet


def generate_key() -> bytes:
    return Fernet.generate_key()


def encrypt_message(key: bytes, message: bytes):
    cipher_suite = Fernet(key)
    ciphertext = cipher_suite.encrypt(message)
    return ciphertext


def decrypt_message(key: bytes, ciphertext: bytes) -> bytes:
    cipher_suite = Fernet(key)
    decrypted_message = cipher_suite.decrypt(ciphertext)
    return decrypted_message
