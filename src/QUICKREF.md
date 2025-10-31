# DNS Covert Channel - Quick Reference

## Installation

```bash
pip install dnspython
```

## Encoding Messages

### Print Query (No Sending)
```bash
python main.py --channel base32 --data "Hello World" --mode print
```

### Send Query
```bash
python main.py --channel base32 --data "Hello World" --mode send --dns-server 8.8.8.8
```

### With Encryption
```bash
python main.py --channel xor --data "secret" --key "MyKey" --mode print
```

## Decoding Messages

### Quick Decode
```bash
# From the encoded part only
python decode.py --channel base32 --encoded "jbswy3dpeblw64tmmq"
```

### From Full Query
```bash
# Automatically extracts encoded part
python decode.py --channel base32 --query "jbswy3dpeblw64tmmq.example.com"
```

### Decode Encrypted
```bash
python decode.py --channel xor --encoded "mruxm3djmzrdgzjsmq" --key "MyKey"
```

### Interactive Mode (Best for Testing!)
```bash
python decode.py --channel base32 --interactive
```

## Complete Workflow

```bash
# 1. Encode
python main.py --channel base32 --data "test message" --mode print

# Output shows:
# Query Name: mruxm3djmzrdgzjsmqxg65a.example.com

# 2. Decode
python decode.py --channel base32 --encoded "mruxm3djmzrdgzjsmqxg65a"

# Output:
# test message
```

## Available Channels

| Channel | Description | Encryption | Usage |
|---------|-------------|------------|-------|
| `base32` | Base32 encoding | No | Best for general use |
| `hex` | Hexadecimal | No | Simple, human-readable |
| `xor` | XOR + Base32 | Yes | Requires `--key` parameter |

## Common Options

### Encoder (main.py)
```bash
--channel base32|hex|xor   # Required
--data "message"            # Required
--mode print|send|both      # Default: print
--dns-server 8.8.8.8        # Default: 8.8.8.8
--domain example.com        # Default: example.com
--qtype A|TXT|AAAA         # Default: A
--key "encryption_key"      # For xor channel
--use-tcp                   # Use TCP instead of UDP
--verbose                   # Show details
```

### Decoder (decode.py)
```bash
--channel base32|hex|xor   # Required
--encoded "encodeddata"     # Encoded string
--query "full.query.com"    # Or full query name
--key "encryption_key"      # For xor channel
--interactive               # Interactive mode
--output text|hex|raw       # Output format
```

## Examples

### Example 1: Simple Message
```bash
# Encode
python main.py --channel base32 --data "Hi there" --mode print

# Decode
python decode.py --channel base32 --encoded "jbxw4zjsfyfa"
```

### Example 2: Encrypted Message
```bash
# Encode
python main.py --channel xor --data "secret info" --key "password" --mode print

# Decode (must use same key!)
python decode.py --channel xor --encoded "ENCODED_STRING" --key "password"
```

### Example 3: Send Real Query
```bash
# Send to Google DNS
python main.py --channel base32 --data "test" --mode send --dns-server 8.8.8.8

# Use different domain
python main.py --channel base32 --data "test" --mode send --domain "google.com"
```

### Example 4: TXT Records
```bash
python main.py --channel base32 --data "TXT data" --qtype TXT --mode print
```

### Example 5: TCP Protocol
```bash
python main.py --channel base32 --data "test" --mode send --use-tcp
```

## Tips

1. **Always use same channel and key for encode/decode**
   - If you encode with `--channel xor --key "abc"`, decode with same parameters

2. **No sudo required!**
   - dnspython doesn't need root privileges

3. **Interactive mode is easiest for testing**
   ```bash
   python decode.py --channel base32 --interactive
   ```

4. **Extract encoded part from query name**
   - Query: `encoded123.example.com`
   - Encoded part: `encoded123`
   - Or use: `--query "encoded123.example.com"`

5. **Check query before sending**
   - Use `--mode print` first to see what will be sent
   - Then use `--mode send` to actually send

## Troubleshooting

**Q: How do I decode a message?**
```bash
python decode.py --channel SAME_CHANNEL --encoded "PASTE_ENCODED_PART"
```

**Q: Forgot the encryption key?**
- Can't decode without the correct key for XOR channel

**Q: Query timeout?**
- Try different DNS server: `--dns-server 1.1.1.1`
- Increase timeout: `--timeout 10`
- Use TCP: `--use-tcp`

**Q: Module not found?**
```bash
pip install dnspython
```

## Getting Help

```bash
# List available channels
python main.py --list-channels

# Show help for encoder
python main.py --help

# Show help for decoder
python decode.py --help

# Run examples
python example.py

# Run demo
./demo.sh
```
