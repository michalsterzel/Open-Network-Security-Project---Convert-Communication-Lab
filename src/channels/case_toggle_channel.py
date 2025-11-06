"""
Case Toggle Covert Channel Implementation.

This channel encodes data by toggling uppercase/lowercase characters in domain names.
DNS is case-insensitive by RFC, but the case is preserved in queries and can be
observed on the wire.

Each character encodes 1 bit:
- Lowercase = 0
- Uppercase = 1

Query-based: data is encoded in the DNS query itself.

Configuration options:
- base_label: base label to encode into (default: "data")
- preserve_dots: if True, only encode in alphanumeric chars (default: True)
"""

from covert_channel_base import CovertChannel


class CaseToggleChannel(CovertChannel):
    """Covert channel using case toggling in DNS labels.
    
    Encodes binary data by varying the case of characters in a domain label.
    Each character position encodes 1 bit (lower=0, upper=1).
    
    Example:
        Data: b'A' (0x41 = 01000001 in binary)
        Encodes to: "dAtaaaaa" (lowercase=0, uppercase=1)
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.base_label = self.config.get('base_label', 'data')
        self.preserve_dots = self.config.get('preserve_dots', True)
    
    def encode(self, data: bytes) -> str:
        """Encode bytes into a case-toggled domain label.
        
        Returns a domain label where case encodes the bits.
        """
        # Convert bytes to bit string
        bits = ''.join(format(byte, '08b') for byte in data)
        
        # Create a base string of sufficient length (use base_label repeated)
        base = (self.base_label * ((len(bits) // len(self.base_label)) + 1))[:len(bits)]
        
        # Apply case based on bits
        result = []
        for i, bit in enumerate(bits):
            char = base[i]
            if char.isalpha():
                if bit == '1':
                    result.append(char.upper())
                else:
                    result.append(char.lower())
            else:
                # Non-alpha characters remain unchanged
                result.append(char)
        
        return ''.join(result)
    
    def decode(self, encoded_data: str) -> bytes:
        """Decode a case-toggled label back to bytes.
        
        Extracts bits from character case (lower=0, upper=1).
        """
        bits = ''
        
        for char in encoded_data:
            if char.isalpha():
                if char.isupper():
                    bits += '1'
                else:
                    bits += '0'
        
        # Convert bits to bytes
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i + 8]
            if len(byte_bits) == 8:
                result.append(int(byte_bits, 2))
        
        return bytes(result)
    
    def bytes_per_query(self) -> float:
        """Return approximate bytes encoded per query."""
        # Depends on base_label length; assume 8 chars minimum
        return 1.0  # ~1 byte per query (8 bits = 8 chars)
    
    def get_description(self) -> str:
        return """Case Toggle Covert Channel

Encodes data by toggling uppercase/lowercase in domain labels.
Each character encodes 1 bit (lowercase=0, uppercase=1).

Characteristics:
- 1 bit per character
- ~1 byte per 8-character label
- Query-based (data in request)
- Very covert (case is rarely monitored)
- DNS is case-insensitive by RFC, but case is preserved

Example: "Hi" (2 bytes = 16 bits) encoded as 16-character label
"""
