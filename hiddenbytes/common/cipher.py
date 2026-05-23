"""
XOR-based encryption/decryption module.

Provides a simple stream cipher using XOR with a randomly generated key.
The key is appended to the ciphertext for self-contained decryption.
"""

import random
import string


class XORCipher:
    """Simple XOR-based encryption/decryption using a derived key.

    Encrypts data by XORing each byte with a byte from the key cyclically.
    The key is appended to the output after a delimiter so the payload is
    self-contained and decryptable at runtime.

    Usage:
        cipher = XORCipher()
        encrypted = cipher.encrypt(b"hello")
        decrypted = XORCipher.decrypt(encrypted)
    """

    KEY_SEPARATOR = b'||KEY||'

    def __init__(self, key=None):
        if key is None:
            self.key = self._generate_key(32)
        else:
            self.key = key.encode() if isinstance(key, str) else key

    @staticmethod
    def _generate_key(length=32):
        """Generate a random alphanumeric key of the given length."""
        return ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        ).encode()

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using XOR and append the key."""
        key_len = len(self.key)
        encrypted = bytearray(len(data))
        for i in range(len(data)):
            encrypted[i] = data[i] ^ self.key[i % key_len]
        return bytes(encrypted) + self.KEY_SEPARATOR + self.key

    @staticmethod
    def decrypt(data: bytes) -> bytes:
        """Decrypt XOR-encrypted data (key must be appended after separator)."""
        sep = XORCipher.KEY_SEPARATOR
        sep_idx = data.rfind(sep)
        if sep_idx == -1:
            raise ValueError("Invalid encrypted data: key separator not found")

        encrypted_data = data[:sep_idx]
        key = data[sep_idx + len(sep):]

        key_len = len(key)
        decrypted = bytearray(len(encrypted_data))
        for i in range(len(encrypted_data)):
            decrypted[i] = encrypted_data[i] ^ key[i % key_len]
        return bytes(decrypted)
