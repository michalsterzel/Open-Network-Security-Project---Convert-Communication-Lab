"""
XOR + Base32 Covert Channel Implementation.
Applies XOR encryption before base32 encoding for obfuscation.
"""

import base64
from covert_channel_base import CovertChannel


class XORBase32Channel(CovertChannel):
    """
    Covert channel using XOR encryption + Base32 encoding.

    Applies XOR cipher with a key before encoding to base32.
    Provides basic encryption for data confidentiality.
    """

    def __init__(self, config: dict = None):
        """
        Initialize with XOR key.

        Args:
            config: Configuration dict with 'key' parameter (bytes or string)
        """
        super().__init__(config)

        # Get key from config or use default
        key = self.config.get('key', b'SecretKey123')

        if isinstance(key, str):
            key = key.encode('utf-8')

        self.key = key

    def _xor_cipher(self, data: bytes) -> bytes:
        """
        Apply XOR cipher with the configured key.

        Args:
            data: Data to encrypt/decrypt

        Returns:
            XOR-ed data
        """
        if not self.key:
            return data

        # XOR each byte with corresponding key byte (cycling through key)
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[i % len(self.key)])

        return bytes(result)

    def encode(self, data: bytes) -> str:
        """
        XOR encrypt data and encode with base32.

        Args:
            data: Raw bytes to encode

        Returns:
            Base32-encoded string
        """
        # First apply XOR encryption
        encrypted = self._xor_cipher(data)

        # Then encode to base32
        encoded = base64.b32encode(encrypted).decode('ascii')
        encoded = encoded.rstrip('=').lower()

        return encoded

    def decode(self, encoded_data: str) -> bytes:
        """
        Decode base32 and XOR decrypt data.

        Args:
            encoded_data: Base32-encoded string

        Returns:
            Original raw bytes
        """
        # First decode from base32
        encoded_data = encoded_data.upper()
        padding = (8 - len(encoded_data) % 8) % 8
        encoded_data += '=' * padding

        encrypted = base64.b32decode(encoded_data)

        # Then apply XOR decryption (XOR is symmetric)
        decrypted = self._xor_cipher(encrypted)

        return decrypted
