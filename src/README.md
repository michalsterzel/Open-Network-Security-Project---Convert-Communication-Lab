# DNS Covert Channel Tool

A modular python3 toolkit for creating and sending DNS queries with embedded covert channels. This tool allows you to hide data within DNS queries using various encoding schemes.

## Features

- **Modular architecture** for easy addition of new covert channels
- **Multiple encoding schemes** (Base32, Hex, XOR+Base32)
- **Print-only mode** to inspect queries without sending
- **Send mode** for actual DNS queries
- **No sudo/root required!** Uses dnspython3 library
- Support for **various DNS query types** (A, AAAA, TXT, etc.)
- **TCP and UDP** protocol support
- Configurable encryption/encoding parameters

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install dnspython3 scapy
```

### Permissions

**Most channels (base32, hex, xor)**: No special permissions needed! Uses dnspython3 which works at the DNS protocol level.

**TTL channel**: Requires root/sudo privileges and Scapy library for raw socket access to control IP-level TTL values.

```bash
# Regular channels - no sudo needed
python3 main.py --channel base32 --data "test" --mode send

# TTL channel - requires sudo
sudo python3 main.py --channel ttl --data "test" --mode send
```

## Usage

### Basic Examples

#### 1. Print Query Only (No Sending)

```bash
python3 main.py --channel base32 --data "Hello World" --mode print
```

#### 2. Send Query to DNS Server

```bash
python3 main.py --channel base32 --data "secret message" --mode send
```

#### 3. Print and Send

```bash
python3 main.py --channel hex --data "test123" --mode both
```

### Advanced Examples

#### Using XOR Encryption with Custom Key

```bash
python3 main.py --channel xor --data "secret" --key "MySecretKey" --mode print
```

#### TXT Record Queries

```bash
python3 main.py --channel base32 --data "data" --qtype TXT --mode send
```

#### Using TCP Instead of UDP

```bash
python3 main.py --channel base32 --data "test" --mode send --use-tcp
```

#### Verbose Output

```bash
python3 main.py --channel base32 --data "test" --mode send --verbose
```

#### TTL Channel (Multi-Query, Requires Sudo)

```bash
# Print TTL queries (shows what TTL values will be used)
python3 main.py --channel ttl --data "Hi" --mode print

# Send with actual TTL encoding (requires Scapy and sudo)
sudo python3 main.py --channel ttl --data "Hi" --mode send

```

### List Available Channels

```bash
python3 main.py --list-channels
```

## Decoding Messages

After encoding a message, you can decode it using the [decode.py](decode.py) script:

### Quick Decode

When you see a query like `jbswy3dpeblw64tmmq.example.com`, decode the encoded part:

```bash
python3 decode.py --channel base32 --encoded "jbswy3dpeblw64tmmq"
```

### Decode Encrypted Messages

For XOR-encrypted messages, you need the same key:

```bash
python3 decode.py --channel xor --encoded "mruxm3djmzrdgzjsmq" --key "MyKey123"
```

### Decode TTL Values

For TTL channel, decode the comma-separated TTL values:

```bash
# From TTL query output
python3 decode.py --channel ttl --encoded "TTL:72,105"

# Or just the values
python3 decode.py --channel ttl --encoded "72,105"

# Output: Hi
```

### Interactive Mode (Recommended!)

The easiest way to decode multiple messages:

```bash
python3 decode.py --channel base32 --interactive
```

Then paste encoded data when prompted.

### Complete Workflow Example

```bash
# 1. Create and print a query
python3 main.py --channel base32 --data "Hello World" --mode print

# Output shows: Query Name: jbswy3dpeblw64tmmq.example.com

# 2. Decode it
python3 decode.py --channel base32 --encoded "jbswy3dpeblw64tmmq"

# Output: Hello World
```

## Command-Line Options

### main.py (Encoder)

| Option | Description | Default |
|--------|-------------|---------|
| `--channel` | Covert channel to use (base32, hex, xor) | Required |
| `--data` | Data to encode and send | Required |
| `--mode` | Operation mode: print, send, or both | print |
| `--dns-server` | DNS server IP address | Default for lab |
| `--domain` | Base domain for DNS query | example.com |
| `--qtype` | DNS query type (A, AAAA, TXT, etc.) | A |
| `--key` | Encryption key for channels that support it | None |
| `--timeout` | Response timeout in seconds | 2 |
| `--use-tcp` | Use TCP instead of UDP | False |
| `--verbose` | Show verbose query details | False |
| `--list-channels` | List all available covert channels | - |

### decode.py (Decoder)

| Option | Description | Default |
|--------|-------------|---------|
| `--channel` | Covert channel used for encoding | Required |
| `--encoded` | Encoded data to decode | - |
| `--query` | Full DNS query name (auto-extracts encoded part) | - |
| `--domain` | Base domain to strip from query | example.com |
| `--key` | Decryption key (for xor channel) | None |
| `--interactive` | Run in interactive mode | False |
| `--output` | Output format: text, hex, or raw | text |

## Architecture

### Core Components

#### 1. `covert_channel_base.py`
Abstract base class defining the interface for all covert channels.

```python3
class CovertChannel(ABC):
    @abstractmethod
    def encode(self, data: bytes) -> str:
        """Encode data into DNS-compatible format"""
        pass

    @abstractmethod
    def decode(self, encoded_data: str) -> bytes:
        """Decode DNS data back to original bytes"""
        pass
```

#### 2. `dns_packet_builder.py`
Builds DNS queries with embedded covert channel data using dnspython3.

#### 3. `dns_sender.py`
Handles query printing and sending with configurable modes (UDP/TCP).

#### 4. `channels/`
Directory containing covert channel implementations.

### Available Covert Channels

#### Base32Channel (`base32`)
- Uses Base32 encoding (RFC 4648)
- DNS-safe characters only (A-Z, 2-7)
- Good balance of efficiency and compatibility
- No encryption

#### HexChannel (`hex`)
- Hexadecimal encoding
- Simple and human-readable
- Less efficient than Base32
- No encryption

#### XORBase32Channel (`xor`)
- XOR encryption + Base32 encoding
- Provides basic data confidentiality
- Configurable encryption key
- Use `--key` option to specify key

#### TTLChannel (`ttl`)
- Encodes data into TTL (Time-To-Live) values
- **Very covert** - TTL is rarely monitored for data exfiltration
- 1 byte per DNS query (requires multiple queries)
- **Uses Scapy** for raw socket access to control IP-level TTL
- **Requires root/sudo** privileges to send packets
- Proper implementation with actual TTL encoding

**TTL Channel Characteristics:**
- Each byte → one TTL value (1-255)
- Example: "Hi" (2 bytes) = 2 queries with TTL=72, TTL=105
- Can use offset and markers for obfuscation
- Very slow but extremely covert
- **Requires Scapy**: `pip install scapy`
- **Requires sudo**: `sudo python3 main.py --channel ttl ...`

## Creating a New Covert Channel

Adding a new covert channel is simple:

### Step 1: Create Your Channel File

Create a new file in `channels/` directory (e.g., `channels/my_channel.py`):

```python3
from covert_channel_base import CovertChannel

class MyChannel(CovertChannel):
    """
    My custom covert channel implementation.
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        # Initialize your channel

    def encode(self, data: bytes) -> str:
        """Encode data for DNS embedding"""
        # Your encoding logic here
        encoded = # ... your encoding ...
        return encoded

    def decode(self, encoded_data: str) -> bytes:
        """Decode DNS data back to bytes"""
        # Your decoding logic here
        decoded = # ... your decoding ...
        return decoded
```

### Step 2: Register Your Channel

Add your channel to `channels/__init__.py`:

```python3
from channels.my_channel import MyChannel

__all__ = [
    'Base32Channel',
    'HexChannel',
    'XORBase32Channel',
    'MyChannel',  # Add your channel here
]
```

### Step 3: Add to Main Script

Add your channel to the `CHANNELS` dictionary in `main.py`:

```python3
CHANNELS = {
    'base32': Base32Channel,
    'hex': HexChannel,
    'xor': XORBase32Channel,
    'mychannel': MyChannel,  # Add your channel
}
```

### Step 4: Use Your Channel

```bash
python3 main.py --channel mychannel --data "test" --mode print
```

## Security Considerations

This tool is designed for educational and research purposes in defensive security:

- Understanding DNS covert channels for detection
- Testing IDS/IPS systems
- Security analysis and monitoring
- Network forensics training

**Important**: Use only in authorized testing environments. Unauthorized use may violate laws and regulations.
