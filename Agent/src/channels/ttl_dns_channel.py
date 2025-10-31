"""
DNS-TTL Covert Channel Implementation.

This channel encodes data into the DNS TTL value of resource records
in DNS responses. Unlike IP TTL, DNS TTL is measured in seconds and is
used by resolvers to cache responses. This channel maps bytes to TTL
values (seconds) and back.

Caveats:
- DNS TTL is an application-layer field; it must be set on the DNS
  server's response (or forged responses) rather than the IP header.
- Many caches and recursive resolvers may override or reduce TTLs; this
  channel is best used in controlled lab networks (like the provided lab).

Encoding format:
- Returns strings in the format "DNS-TTL:val1,val2,..." where each val
  represents seconds to put in the DNS TTL field for sequential responses.

Configuration options (via config dict):
- offset: integer added to every byte (default: 0)
- marker_start: optional TTL value used as a start marker
- marker_end: optional TTL value used as an end marker
"""

from typing import List
from covert_channel_base import CovertChannel


class TTLDNSChannel(CovertChannel):
    """Covert channel using DNS TTL (seconds) values.

    Each byte of data maps to a TTL value (recommended range 1-65535 but
    typical DNS TTLs are in seconds; this implementation keeps values in
    1-65535 to be safe). The encode/decode APIs mirror other channel classes.
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.offset = int(self.config.get('offset', 0))
        self.marker_start = self.config.get('marker_start', None)
        self.marker_end = self.config.get('marker_end', None)

    def encode(self, data: bytes) -> str:
        """Encode bytes into DNS TTL values (seconds).

        Returns a string: "DNS-TTL:val1,val2,..."
        """
        ttl_values: List[int] = []

        if self.marker_start is not None:
            ttl_values.append(int(self.marker_start))

        for b in data:
            # Map byte (0-255) to a TTL value and add offset.
            ttl = (b + self.offset) % 65536
            if ttl == 0:
                ttl = 1
            ttl_values.append(ttl)

        if self.marker_end is not None:
            ttl_values.append(int(self.marker_end))

        return "DNS-TTL:" + ",".join(str(x) for x in ttl_values)

    def decode(self, encoded_data: str) -> bytes:
        """Decode a "DNS-TTL:..." string back to bytes.

        Accepts values with or without the prefix.
        """
        if encoded_data.startswith("DNS-TTL:"):
            encoded_data = encoded_data[len("DNS-TTL:"):]

        parts = [p.strip() for p in encoded_data.split(',') if p.strip()]
        ttl_values = [int(x) for x in parts]

        # Strip markers
        if self.marker_start is not None and ttl_values and ttl_values[0] == int(self.marker_start):
            ttl_values = ttl_values[1:]
        if self.marker_end is not None and ttl_values and ttl_values[-1] == int(self.marker_end):
            ttl_values = ttl_values[:-1]

        result = bytearray()
        for ttl in ttl_values:
            b = (ttl - self.offset) % 256
            result.append(b)

        return bytes(result)

    def get_ttl_values(self, data: bytes) -> List[int]:
        encoded = self.encode(data)
        if encoded.startswith("DNS-TTL:"):
            encoded = encoded[len("DNS-TTL:"):]
        return [int(x.strip()) for x in encoded.split(',') if x.strip()]

    def bytes_per_query(self) -> int:
        return 1

    def get_description(self) -> str:
        return """DNS-TTL Covert Channel

Encodes data into DNS TTL seconds in resource records. Use only in
controlled environments where you can control DNS responses.
"""
