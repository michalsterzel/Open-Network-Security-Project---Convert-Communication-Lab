"""
Label Count Covert Channel Implementation.

This channel encodes data by varying the number of labels (subdomain depth)
in DNS queries.

Example:
- 1 label  (example.com) = value 0
- 2 labels (a.example.com) = value 1
- 3 labels (a.b.example.com) = value 2
- 4 labels (a.b.c.example.com) = value 3
...

Query-based: data is encoded in the DNS query structure itself.

Configuration options:
- min_labels: minimum number of subdomain labels (default: 1)
- max_labels: maximum number of subdomain labels (default: 8)
- label_prefix: prefix for generated labels (default: "sub")
"""

from covert_channel_base import CovertChannel
import math


class LabelCountChannel(CovertChannel):
    """Covert channel using subdomain label count.
    
    Encodes data by varying the depth of subdomains.
    The number of labels before the base domain encodes a value.
    
    Example with min=1, max=8:
        8 possible values = 3 bits per query
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.min_labels = self.config.get('min_labels', 1)
        self.max_labels = self.config.get('max_labels', 8)
        self.label_prefix = self.config.get('label_prefix', 'sub')
        
        # Calculate bits per query
        self.num_values = self.max_labels - self.min_labels + 1
        self.bits_per_query = int(math.log2(self.num_values))
    
    def encode(self, data: bytes) -> str:
        """Encode bytes into a sequence of label counts.
        
        Returns format: "LABELCOUNT:2,3,1,4,..."
        Each number represents the number of subdomain labels to use.
        """
        # Convert bytes to bits
        bits = ''.join(format(byte, '08b') for byte in data)
        
        # Split into chunks
        chunk_size = self.bits_per_query
        label_counts = []
        
        for i in range(0, len(bits), chunk_size):
            chunk = bits[i:i + chunk_size]
            
            # Pad last chunk if needed
            if len(chunk) < chunk_size:
                chunk = chunk.ljust(chunk_size, '0')
            
            # Convert to value and add min_labels offset
            value = int(chunk, 2)
            label_count = min(value + self.min_labels, self.max_labels)
            label_counts.append(str(label_count))
        
        return "LABELCOUNT:" + ",".join(label_counts)
    
    def decode(self, encoded_data: str) -> bytes:
        """Decode a sequence of label counts back to bytes.
        
        Accepts format: "LABELCOUNT:2,3,1,..." or just "2,3,1,..."
        """
        # Remove prefix if present
        if encoded_data.startswith("LABELCOUNT:"):
            encoded_data = encoded_data[len("LABELCOUNT:"):]
        
        # Parse label counts
        label_counts = [int(x.strip()) for x in encoded_data.split(',') if x.strip()]
        
        # Convert to bits
        bits = ''
        for count in label_counts:
            value = count - self.min_labels
            value = max(0, min(value, self.num_values - 1))
            bits += format(value, f'0{self.bits_per_query}b')
        
        # Convert bits to bytes
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i + 8]
            if len(byte_bits) == 8:
                result.append(int(byte_bits, 2))
        
        return bytes(result)
    
    def build_query_name(self, label_count: int, base_domain: str) -> str:
        """Build a query name with the specified number of labels.
        
        Args:
            label_count: Number of subdomain labels to include
            base_domain: Base domain (e.g., "example.com")
        
        Returns:
            Full query name (e.g., "sub1.sub2.sub3.example.com")
        """
        if label_count < 1:
            return base_domain
        
        labels = [f"{self.label_prefix}{i+1}" for i in range(label_count)]
        return ".".join(labels) + "." + base_domain
    
    def get_label_counts(self, data: bytes) -> list:
        """Get the sequence of label counts for the given data.
        
        Useful for building DNS queries.
        """
        encoded = self.encode(data)
        if encoded.startswith("LABELCOUNT:"):
            encoded = encoded[len("LABELCOUNT:"):]
        return [int(x.strip()) for x in encoded.split(',') if x.strip()]
    
    def bytes_per_query(self) -> float:
        """Return approximate bytes encoded per query."""
        return self.bits_per_query / 8.0
    
    def get_description(self) -> str:
        return f"""Label Count Covert Channel

Encodes data by varying the number of subdomain labels.

Characteristics:
- {self.bits_per_query} bits per query ({self.num_values} label depths available)
- ~{self.bytes_per_query():.2f} bytes per query
- Range: {self.min_labels}-{self.max_labels} labels
- Query-based (data in request structure)
- Moderately covert (varying depth is somewhat normal)

Example: "Hi" (2 bytes = 16 bits) = {16 // self.bits_per_query} queries needed

Query examples:
- 1 label: sub1.example.com
- 3 labels: sub1.sub2.sub3.example.com
"""
