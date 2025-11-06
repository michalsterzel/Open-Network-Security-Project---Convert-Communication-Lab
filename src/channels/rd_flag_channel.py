"""
RD Flag (Recursion Desired) Covert Channel Implementation.

This channel encodes data by toggling the Recursion Desired (RD) flag
in DNS queries.

Each query encodes 1 bit:
- RD flag set (1) = bit 1
- RD flag cleared (0) = bit 0

Query-based: data is encoded in the DNS query header flags.

Configuration options:
- invert: if True, invert the bit meaning (default: False)
"""

from covert_channel_base import CovertChannel


class RDFlagChannel(CovertChannel):
    """Covert channel using DNS Recursion Desired (RD) flag.
    
    Encodes data by toggling the RD flag bit in DNS queries.
    Each query encodes 1 bit.
    
    Example:
        Data: b'A' (0x41 = 01000001 binary)
        Requires: 8 queries with RD flags: 0,1,0,0,0,0,0,1
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.invert = self.config.get('invert', False)
    
    def encode(self, data: bytes) -> str:
        """Encode bytes into a sequence of RD flag values.
        
        Returns format: "RD:0,1,1,0,1,0,0,1,..."
        Each value is the RD flag state (0 or 1).
        """
        # Convert bytes to bits
        bits = ''.join(format(byte, '08b') for byte in data)
        
        # Optionally invert
        if self.invert:
            bits = ''.join('1' if b == '0' else '0' for b in bits)
        
        # Convert to comma-separated values
        rd_values = ','.join(bits)
        
        return "RD:" + rd_values
    
    def decode(self, encoded_data: str) -> bytes:
        """Decode a sequence of RD flag values back to bytes.
        
        Accepts format: "RD:0,1,1,0,..." or just "0,1,1,0,..."
        """
        # Remove prefix if present
        if encoded_data.startswith("RD:"):
            encoded_data = encoded_data[len("RD:"):]
        
        # Parse flag values
        bits = encoded_data.replace(',', '').replace(' ', '')
        
        # Optionally invert
        if self.invert:
            bits = ''.join('1' if b == '0' else '0' for b in bits)
        
        # Convert bits to bytes
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i + 8]
            if len(byte_bits) == 8:
                result.append(int(byte_bits, 2))
        
        return bytes(result)
    
    def get_rd_flags(self, data: bytes) -> list:
        """Get the sequence of RD flag values for the given data.
        
        Returns list of booleans (True=RD set, False=RD cleared).
        Useful for building DNS queries.
        """
        encoded = self.encode(data)
        if encoded.startswith("RD:"):
            encoded = encoded[len("RD:"):]
        
        bits = encoded.replace(',', '').replace(' ', '')
        return [bit == '1' for bit in bits]
    
    def bytes_per_query(self) -> float:
        """Return bytes encoded per query."""
        return 0.125  # 1 bit = 1/8 byte per query
    
    def get_description(self) -> str:
        return """RD Flag (Recursion Desired) Covert Channel

Encodes data by toggling the Recursion Desired flag in DNS queries.
Each query encodes 1 bit.

Characteristics:
- 1 bit per query (8 queries per byte)
- Low bandwidth
- Query-based (data in request header)
- Very covert (RD flag variation is normal)
- Works through most resolvers

The RD flag indicates whether the client wants the server to recursively
resolve the query. Toggling it between queries is a subtle covert channel.

Example: "Hi" (2 bytes = 16 bits) = 16 queries needed

Bit sequence for 'H' (0x48 = 01001000):
Query 1: RD=0
Query 2: RD=1
Query 3: RD=0
Query 4: RD=0
Query 5: RD=1
Query 6: RD=0
Query 7: RD=0
Query 8: RD=0
"""
