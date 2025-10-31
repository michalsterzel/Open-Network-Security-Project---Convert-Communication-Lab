"""
TXID (Transaction ID) Covert Channel Implementation.

This channel encodes data into the DNS transaction ID (TXID) field.
The TXID is a 16-bit field in DNS queries used to match requests with responses.

Each query can encode 16 bits (2 bytes) of data in the TXID.

Query-based: data is encoded in the DNS query header.

Configuration options:
- randomize_unused: if True, randomize bits beyond data length (default: False)
- preserve_high_bit: some implementations check the high bit (default: False)
"""

from covert_channel_base import CovertChannel
import struct


class TXIDChannel(CovertChannel):
    """Covert channel using DNS Transaction ID field.
    
    Encodes data by setting specific TXID values in DNS queries.
    Each query encodes 16 bits (2 bytes) in the TXID field.
    
    Example:
        Data: b'Hi' (0x4869 = 18537 decimal)
        TXID: 18537 (0x4869)
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.randomize_unused = self.config.get('randomize_unused', False)
        self.preserve_high_bit = self.config.get('preserve_high_bit', False)
    
    def encode(self, data: bytes) -> str:
        """Encode bytes into a sequence of TXID values.
        
        Returns format: "TXID:12345,23456,34567,..."
        Each TXID encodes 2 bytes (16 bits).
        """
        txid_values = []
        
        # Process data in 2-byte chunks
        for i in range(0, len(data), 2):
            chunk = data[i:i+2]
            
            # Pad last chunk if needed
            if len(chunk) < 2:
                chunk = chunk + b'\x00' * (2 - len(chunk))
            
            # Convert 2 bytes to 16-bit unsigned integer
            txid = struct.unpack('>H', chunk)[0]
            
            # Optionally preserve high bit (some systems use it)
            if self.preserve_high_bit:
                txid = txid & 0x7FFF  # Clear high bit
            
            txid_values.append(str(txid))
        
        return "TXID:" + ",".join(txid_values)
    
    def decode(self, encoded_data: str) -> bytes:
        """Decode a sequence of TXID values back to bytes.
        
        Accepts format: "TXID:12345,23456,..." or just "12345,23456,..."
        """
        # Remove prefix if present
        if encoded_data.startswith("TXID:"):
            encoded_data = encoded_data[len("TXID:"):]
        
        # Parse TXID values
        txid_values = [int(x.strip()) for x in encoded_data.split(',') if x.strip()]
        
        # Convert TXIDs to bytes
        result = bytearray()
        for txid in txid_values:
            # Convert 16-bit integer to 2 bytes (big-endian)
            result.extend(struct.pack('>H', txid & 0xFFFF))
        
        return bytes(result)
    
    def get_txid_values(self, data: bytes) -> list:
        """Get the sequence of TXID values for the given data.
        
        Useful for building DNS queries with specific TXIDs.
        """
        encoded = self.encode(data)
        if encoded.startswith("TXID:"):
            encoded = encoded[len("TXID:"):]
        return [int(x.strip()) for x in encoded.split(',') if x.strip()]
    
    def bytes_per_query(self) -> float:
        """Return bytes encoded per query."""
        return 2.0  # 16 bits = 2 bytes per query
    
    def get_description(self) -> str:
        return """TXID (Transaction ID) Covert Channel

Encodes data into the DNS transaction ID field.
Each query encodes 16 bits (2 bytes) in the TXID.

Characteristics:
- 16 bits (2 bytes) per query
- High bandwidth covert channel
- Query-based (data in request header)
- Somewhat covert (TXID variation is normal)
- Some resolvers/firewalls may randomize TXIDs

Caveats:
- Recursive resolvers often override TXIDs
- NAT/firewalls may modify TXIDs for security
- Best used in direct query scenarios

Example: "Hi" (2 bytes) = 1 query needed
         "Hello" (5 bytes) = 3 queries needed
"""
