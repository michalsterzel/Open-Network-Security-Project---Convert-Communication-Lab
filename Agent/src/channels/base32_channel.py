"""
Base32 Covert Channel Implementation.
Encodes data using base32 encoding for DNS subdomain embedding.
"""

import base64
from covert_channel_base import CovertChannel


class Base32Channel(CovertChannel):
    """
    Covert channel using Base32 encoding.

    Base32 is DNS-safe as it only uses characters A-Z and 2-7.
    This makes it ideal for encoding data in DNS subdomain labels.
    """

    def encode(self, data: bytes) -> str:
        """
        Encode data using base32 encoding.

        Args:
            data: Raw bytes to encode

        Returns:
            Base32-encoded string (lowercase, without padding)
        """
        # Encode to base32 and remove padding
        encoded = base64.b32encode(data).decode('ascii')
        # Remove padding and convert to lowercase (DNS is case-insensitive)
        encoded = encoded.rstrip('=').lower()
        return encoded

    def decode(self, encoded_data: str) -> bytes:
        """
        Decode base32-encoded data.

        Args:
            encoded_data: Base32-encoded string

        Returns:
            Original raw bytes
        """
        # Uppercase for decoding and add padding
        encoded_data = encoded_data.upper()
        # Add back padding
        padding = (8 - len(encoded_data) % 8) % 8
        encoded_data += '=' * padding

        return base64.b32decode(encoded_data)
