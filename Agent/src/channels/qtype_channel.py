"""
QTYPE (Query Type) Covert Channel Implementation.

This channel encodes data by rotating through different DNS query types.
Each query type (A, AAAA, TXT, MX, etc.) represents a numeric value,
allowing ~4 bits of data per query.

Query-based: data is encoded in the DNS query itself, not the response.

Configuration options:
- types: list of query type names to use (default: common types)
- bits_per_query: number of bits encoded per query (auto-calculated from type count)
"""

from typing import List
from covert_channel_base import CovertChannel


class QTypeChannel(CovertChannel):
    """Covert channel using DNS query type (QTYPE) rotation.
    
    Encodes data by selecting different query types for sequential queries.
    Each type maps to a numeric value (0-N).
    
    Example with 16 types: encodes 4 bits per query
    - A=0, AAAA=1, TXT=2, MX=3, CNAME=4, NS=5, PTR=6, SOA=7,
      SRV=8, CAA=9, DNSKEY=10, DS=11, NAPTR=12, TLSA=13, ANY=14, AXFR=15
    """
    
    # Default query types (16 types = 4 bits per query)
    DEFAULT_TYPES = [
        'A', 'AAAA', 'TXT', 'MX', 'CNAME', 'NS', 'PTR', 'SOA',
        'SRV', 'CAA', 'DNSKEY', 'DS', 'NAPTR', 'TLSA', 'ANY', 'AXFR'
    ]
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.types = self.config.get('types', self.DEFAULT_TYPES.copy())
        self.bits_per_query = self._calculate_bits_per_query()
        
        # Build type-to-value and value-to-type mappings
        self.type_to_value = {t: i for i, t in enumerate(self.types)}
        self.value_to_type = {i: t for i, t in enumerate(self.types)}
    
    def _calculate_bits_per_query(self) -> int:
        """Calculate how many bits can be encoded per query."""
        import math
        return int(math.log2(len(self.types)))
    
    def encode(self, data: bytes) -> str:
        """Encode bytes into a sequence of query types.
        
        Returns format: "QTYPE:A,AAAA,TXT,..."
        Each type represents bits_per_query bits of data.
        This format is for display/decode; actual sending requires multiple queries.
        """
        type_sequence = self.get_qtype_sequence(data)
        return "QTYPE:" + ",".join(type_sequence)
    
    def decode(self, encoded_data: str) -> bytes:
        """Decode a sequence of query types back to bytes.
        
        Accepts format: "QTYPE:A,AAAA,TXT,..." or just "A,AAAA,TXT,..."
        """
        # Remove prefix if present
        if encoded_data.startswith("QTYPE:"):
            encoded_data = encoded_data[len("QTYPE:"):]
        
        # Split into type sequence
        type_sequence = [t.strip().upper() for t in encoded_data.split(',') if t.strip()]
        
        # Convert types to bit string
        bits = ''
        for qtype in type_sequence:
            if qtype in self.type_to_value:
                value = self.type_to_value[qtype]
                bits += format(value, f'0{self.bits_per_query}b')
            else:
                # Unknown type, skip or treat as 0
                bits += '0' * self.bits_per_query
        
        # Convert bits to bytes
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i + 8]
            if len(byte_bits) == 8:
                result.append(int(byte_bits, 2))
        
        return bytes(result)
    
    def get_qtype_sequence(self, data: bytes) -> List[str]:
        """Get the sequence of query types for the given data.
        
        Useful for building DNS queries.
        Returns one query type per chunk of bits.
        """
        # Convert bytes to bits
        bits = ''.join(format(byte, '08b') for byte in data)
        
        # Split into chunks of bits_per_query size
        chunk_size = self.bits_per_query
        type_sequence = []
        
        for i in range(0, len(bits), chunk_size):
            chunk = bits[i:i + chunk_size]
            
            # Pad last chunk if needed
            if len(chunk) < chunk_size:
                chunk = chunk.ljust(chunk_size, '0')
            
            # Convert bit chunk to integer
            value = int(chunk, 2)
            
            # Map to query type
            if value < len(self.types):
                type_sequence.append(self.types[value])
            else:
                # Shouldn't happen with proper chunking
                type_sequence.append(self.types[0])
        
        return type_sequence
    
    def bytes_per_query(self) -> float:
        """Return approximate bytes encoded per query."""
        return self.bits_per_query / 8.0
    
    def get_description(self) -> str:
        return f"""QTYPE (Query Type) Covert Channel

Encodes data by rotating through different DNS query types.

Characteristics:
- {self.bits_per_query} bits per query ({len(self.types)} types available)
- ~{self.bytes_per_query():.2f} bytes per query
- Query-based (data in request, not response)
- Moderately covert (QTYPE variation is somewhat normal)

Available types: {', '.join(self.types[:8])}{'...' if len(self.types) > 8 else ''}

Example: "Hi" (2 bytes = 16 bits) = {16 // self.bits_per_query} queries needed
"""
