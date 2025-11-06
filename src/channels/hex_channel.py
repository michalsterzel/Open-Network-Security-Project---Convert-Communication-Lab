"""
Hexadecimal Covert Channel Implementation.
Encodes data using hexadecimal encoding.
"""

from covert_channel_base import CovertChannel


class HexChannel(CovertChannel):
    """
    Covert channel using hexadecimal encoding.

    Converts data to hex representation for DNS embedding.
    Simple and human-readable, but less efficient than base32.
    """

    def encode(self, data: bytes) -> str:
        """
        Encode data as hexadecimal string.

        Args:
            data: Raw bytes to encode

        Returns:
            Hexadecimal string representation
        """
        return data.hex()

    def decode(self, encoded_data: str) -> bytes:
        """
        Decode hexadecimal string to bytes.

        Args:
            encoded_data: Hexadecimal string

        Returns:
            Original raw bytes
        """
        return bytes.fromhex(encoded_data)
