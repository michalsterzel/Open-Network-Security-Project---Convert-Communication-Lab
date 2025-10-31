"""
TTL (Time-To-Live) Covert Channel Implementation.

This channel encodes data into the TTL field of DNS packets.
Each byte of data is encoded as a TTL value (1-255).

NOTE: TTL encoding requires sending actual DNS packets with custom TTL values.
The dnspython library doesn't directly control IP-level TTL, so this channel
works best when combined with raw socket implementation or when the data is
small enough to encode in multiple sequential queries.

For this implementation, we'll encode data as TTL values that can be embedded
in multiple DNS queries (one byte per query).
"""

from covert_channel_base import CovertChannel
from typing import List


class TTLChannel(CovertChannel):
    """
    Covert channel using TTL (Time-To-Live) values.

    Each byte of data becomes a TTL value (1-255).
    Multiple queries are needed for messages longer than 1 byte.

    Encoding: Each byte directly maps to a TTL value
    Decoding: Extract TTL values from sequential queries

    Example:
        Data: b"Hi" (0x48 0x69 = 72 105 in decimal)
        Encodes to: [TTL=72, TTL=105]
        Requires: 2 DNS queries
    """

    def __init__(self, config: dict = None):
        """
        Initialize TTL channel.

        Args:
            config: Configuration dict with optional parameters:
                - 'offset': Add offset to TTL values (default: 0)
                - 'marker_start': Start marker TTL (default: None)
                - 'marker_end': End marker TTL (default: None)
        """
        super().__init__(config)
        self.offset = self.config.get('offset', 0)
        self.marker_start = self.config.get('marker_start', None)
        self.marker_end = self.config.get('marker_end', None)

    def encode(self, data: bytes) -> str:
        """
        Encode data as TTL values.

        Since TTL is set per-packet (not in query name), this returns
        a special format string that indicates the TTL values needed.

        Format: "TTL:val1,val2,val3,..."

        Args:
            data: Raw bytes to encode

        Returns:
            String in format "TTL:72,105,..." representing TTL values
        """
        ttl_values = []

        # Optional start marker
        if self.marker_start is not None:
            ttl_values.append(str(self.marker_start))

        # Encode each byte as TTL value
        for byte in data:
            # TTL must be 1-255, we add offset and ensure valid range
            ttl = (byte + self.offset) % 256
            if ttl == 0:
                ttl = 1  # TTL cannot be 0
            ttl_values.append(str(ttl))

        # Optional end marker
        if self.marker_end is not None:
            ttl_values.append(str(self.marker_end))

        return "TTL:" + ",".join(ttl_values)

    def decode(self, encoded_data: str) -> bytes:
        """
        Decode TTL values back to original bytes.

        Args:
            encoded_data: String in format "TTL:72,105,..." or just "72,105,..."

        Returns:
            Original raw bytes
        """
        # Remove "TTL:" prefix if present
        if encoded_data.startswith("TTL:"):
            encoded_data = encoded_data[4:]

        # Split by comma
        ttl_values = [int(x.strip()) for x in encoded_data.split(',')]

        # Remove start marker if present
        if self.marker_start is not None and ttl_values[0] == self.marker_start:
            ttl_values = ttl_values[1:]

        # Remove end marker if present
        if self.marker_end is not None and ttl_values[-1] == self.marker_end:
            ttl_values = ttl_values[:-1]

        # Decode TTL values back to bytes
        result = bytearray()
        for ttl in ttl_values:
            # Reverse the offset
            byte = (ttl - self.offset) % 256
            result.append(byte)

        return bytes(result)

    def get_ttl_values(self, data: bytes) -> List[int]:
        """
        Get list of TTL values for the given data.

        This is useful for packet construction.

        Args:
            data: Raw bytes to encode

        Returns:
            List of TTL values (integers 1-255)
        """
        encoded = self.encode(data)
        if encoded.startswith("TTL:"):
            encoded = encoded[4:]
        return [int(x.strip()) for x in encoded.split(',')]

    def bytes_per_query(self) -> int:
        """
        Return how many bytes of data can be encoded per query.

        For TTL channel, it's 1 byte per query (one TTL value per packet).
        """
        return 1

    def get_description(self) -> str:
        """Return description of this covert channel."""
        return """TTL (Time-To-Live) Covert Channel

Encodes data into the TTL field of DNS packets.
Each byte becomes a TTL value (1-255).

Characteristics:
- 1 byte per DNS query
- Very covert (TTL is rarely monitored)
- Requires multiple queries for multi-byte messages
- Can use markers to indicate message boundaries

Configuration options:
- offset: Add offset to TTL values for obfuscation
- marker_start: TTL value to mark message start
- marker_end: TTL value to mark message end

Example: "Hi" (2 bytes) = [TTL=72, TTL=105] = 2 queries needed
"""
