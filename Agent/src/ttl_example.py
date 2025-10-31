#!/usr/bin/env python3
"""
TTL Covert Channel Example

Demonstrates how the TTL covert channel works.
Shows encoding, decoding, and the limitations of the implementation.
"""

from channels import TTLChannel


def example_basic_ttl():
    """Basic TTL channel encoding and decoding."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic TTL Encoding")
    print("="*70)

    # Create TTL channel
    channel = TTLChannel()

    # Encode a simple message
    message = b"Hi"
    print(f"\nOriginal message: {message.decode()}")
    print(f"Message bytes: {[byte for byte in message]}")
    print(f"Message hex: {message.hex()}")

    # Encode
    encoded = channel.encode(message)
    print(f"\nEncoded (TTL format): {encoded}")

    # Get actual TTL values
    ttl_values = channel.get_ttl_values(message)
    print(f"TTL values: {ttl_values}")
    print(f"\nExplanation:")
    print(f"  'H' = ASCII 72 (0x48) → TTL = 72")
    print(f"  'i' = ASCII 105 (0x69) → TTL = 105")
    print(f"\nThis requires 2 DNS queries (one per byte)")

    # Decode
    decoded = channel.decode(encoded)
    print(f"\nDecoded message: {decoded.decode()}")
    print(f"Match: {message == decoded}")


def example_with_offset():
    """TTL channel with offset for obfuscation."""
    print("\n" + "="*70)
    print("EXAMPLE 2: TTL with Offset (Obfuscation)")
    print("="*70)

    # Create TTL channel with offset
    channel = TTLChannel(config={'offset': 10})

    message = b"Hi"
    print(f"\nOriginal message: {message.decode()}")

    # Encode with offset
    encoded = channel.encode(message)
    ttl_values = channel.get_ttl_values(message)

    print(f"\nTTL values WITH offset (+10): {ttl_values}")
    print(f"Explanation:")
    print(f"  'H' = 72 + 10 = 82")
    print(f"  'i' = 105 + 10 = 115")

    # Decode (offset is automatically applied in reverse)
    decoded = channel.decode(encoded)
    print(f"\nDecoded message: {decoded.decode()}")
    print(f"Match: {message == decoded}")


def example_with_markers():
    """TTL channel with start/end markers."""
    print("\n" + "="*70)
    print("EXAMPLE 3: TTL with Markers")
    print("="*70)

    # Create TTL channel with markers
    channel = TTLChannel(config={
        'marker_start': 255,  # TTL=255 marks start
        'marker_end': 1,      # TTL=1 marks end
    })

    message = b"Hi"
    print(f"\nOriginal message: {message.decode()}")

    # Encode with markers
    encoded = channel.encode(message)
    ttl_values = channel.get_ttl_values(message)

    print(f"\nTTL values WITH markers: {ttl_values}")
    print(f"Explanation:")
    print(f"  Query 1: TTL = 255 (START MARKER)")
    print(f"  Query 2: TTL = 72  ('H')")
    print(f"  Query 3: TTL = 105 ('i')")
    print(f"  Query 4: TTL = 1   (END MARKER)")
    print(f"\nTotal queries needed: {len(ttl_values)}")

    # Decode (markers are automatically stripped)
    decoded = channel.decode(encoded)
    print(f"\nDecoded message: {decoded.decode()}")
    print(f"Match: {message == decoded}")


def example_longer_message():
    """TTL channel with longer message."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Longer Message")
    print("="*70)

    channel = TTLChannel()

    message = b"Hello"
    print(f"\nOriginal message: {message.decode()}")
    print(f"Message length: {len(message)} bytes")

    # Encode
    encoded = channel.encode(message)
    ttl_values = channel.get_ttl_values(message)

    print(f"\nTTL values: {ttl_values}")
    print(f"\nCharacter → TTL mapping:")
    for char_byte, ttl in zip(message, ttl_values):
        char = chr(char_byte)
        print(f"  '{char}' (ASCII {char_byte}, 0x{char_byte:02x}) → TTL = {ttl}")

    print(f"\nTotal DNS queries required: {len(ttl_values)}")
    print(f"\nNote: Each query carries only 1 byte of information!")

    # Decode
    decoded = channel.decode(encoded)
    print(f"\nDecoded: {decoded.decode()}")


def example_special_chars():
    """TTL channel with special/non-printable characters."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Special Characters")
    print("="*70)

    channel = TTLChannel()

    # Message with newline and tab
    message = b"A\nB\tC"
    print(f"\nOriginal message: {repr(message)}")
    print(f"Message bytes: {[byte for byte in message]}")

    # Encode
    encoded = channel.encode(message)
    ttl_values = channel.get_ttl_values(message)

    print(f"\nTTL values: {ttl_values}")
    print(f"\nCharacter → TTL mapping:")
    for char_byte, ttl in zip(message, ttl_values):
        if 32 <= char_byte < 127:
            char_repr = f"'{chr(char_byte)}'"
        else:
            char_repr = f"\\x{char_byte:02x}"
        print(f"  {char_repr:8s} (decimal {char_byte:3d}) → TTL = {ttl}")

    # Decode
    decoded = channel.decode(encoded)
    print(f"\nDecoded: {repr(decoded)}")
    print(f"Match: {message == decoded}")


def example_limitations():
    """Demonstrate limitations of the TTL channel."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Limitations and Considerations")
    print("="*70)

    channel = TTLChannel()

    print("\nLimitations of TTL Covert Channel:")
    print("-" * 70)

    print("\n1. EFFICIENCY:")
    message = b"Secret message"
    ttl_count = len(channel.get_ttl_values(message))
    print(f"   Message: '{message.decode()}' ({len(message)} bytes)")
    print(f"   Queries needed: {ttl_count}")
    print(f"   Efficiency: 1 byte per query")

    print("\n2. TTL VALUE RANGE:")
    print(f"   Valid TTL range: 1-255")
    print(f"   Cannot encode byte value 0 (TTL cannot be 0)")
    print(f"   Null bytes (\\x00) are encoded as TTL=1")

    print("\n3. IMPLEMENTATION LIMITATION:")
    print(f"   dnspython cannot set IP-level TTL directly")
    print(f"   The TTL is controlled by the OS network stack")
    print(f"   This implementation shows TTL values conceptually")
    print(f"   For real TTL encoding, raw sockets are required")

    print("\n4. DETECTION:")
    print(f"   Very covert - TTL variations look like routing changes")
    print(f"   Difficult to detect without specific monitoring")
    print(f"   Multiple queries to same domain might be suspicious")

    print("\n5. USE CASES:")
    print(f"   - Very small messages (e.g., status codes, commands)")
    print(f"   - When extreme covertness is required")
    print(f"   - Slow, low-bandwidth exfiltration")
    print(f"   - Demonstration/research purposes")


def main():
    """Run all examples."""
    print("\n")
    print("#" * 70)
    print("# TTL COVERT CHANNEL - EXAMPLES AND DEMONSTRATIONS")
    print("#" * 70)

    example_basic_ttl()
    example_with_offset()
    example_with_markers()
    example_longer_message()
    example_special_chars()
    example_limitations()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
    print("\nTo use TTL channel with main script:")
    print("  python main.py --channel ttl --data 'Hi' --mode print")
    print("\nTo decode TTL values:")
    print("  python decode.py --channel ttl --encoded '72,105'")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
