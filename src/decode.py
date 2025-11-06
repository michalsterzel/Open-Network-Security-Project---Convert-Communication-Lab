#!/usr/bin/env python3
"""
DNS Covert Channel Decoder

This script decodes data that was encoded by the DNS covert channel tool.
Use this to decrypt/decode the subdomain portion of DNS queries.

Usage:
    python decode.py --channel base32 --encoded "jbswy3dpeblw64tmmq"
    python decode.py --channel xor --encoded "mruxm3djmzrdgzjsmq" --key "MyKey"
"""

import argparse
import sys
from typing import Optional

# Import covert channel implementations
from channels import (Base32Channel, HexChannel, XORBase32Channel, TTLChannel, TTLDNSChannel,
                      QTypeChannel, CaseToggleChannel, LabelCountChannel, TXIDChannel, RDFlagChannel, Base32ChannelExercise)


# Available covert channels
CHANNELS = {
    'base32': Base32Channel,
    'base32-exercise': Base32ChannelExercise,
    'hex': HexChannel,
    'xor': XORBase32Channel,
    'ttl': TTLChannel,
    'ttl-dns': TTLDNSChannel,
    'qtype': QTypeChannel,
    'case': CaseToggleChannel,
    'labels': LabelCountChannel,
    'txid': TXIDChannel,
    'rd': RDFlagChannel,
}


def decode_message(channel_name: str, encoded_data: str, config: Optional[dict] = None):
    """
    Decode an encoded message using the specified channel.

    Args:
        channel_name: Name of the channel used to encode
        encoded_data: The encoded string to decode
        config: Optional configuration (e.g., encryption key)

    Returns:
        Decoded bytes
    """
    if channel_name not in CHANNELS:
        print(f"[!] Error: Unknown channel '{channel_name}'")
        print(f"[*] Available channels: {', '.join(CHANNELS.keys())}")
        sys.exit(1)

    # Create channel instance
    channel_class = CHANNELS[channel_name]
    channel = channel_class(config)

    # Decode the data
    try:
        decoded = channel.decode(encoded_data)
        return decoded
    except Exception as e:
        print(f"[!] Error decoding: {e}")
        sys.exit(1)


def extract_encoded_from_query(query_name: str, domain: str) -> str:
    """
    Extract the encoded portion from a full DNS query name.

    Args:
        query_name: Full DNS query (e.g., "encoded123.example.com")
        domain: Base domain (e.g., "example.com")

    Returns:
        Just the encoded part (e.g., "encoded123")
    """
    # Remove the domain suffix
    if query_name.endswith('.' + domain):
        encoded = query_name[:-len('.' + domain)]
    elif query_name.endswith(domain):
        encoded = query_name[:-len(domain)]
        if encoded.endswith('.'):
            encoded = encoded[:-1]
    else:
        # Assume the whole thing is encoded
        encoded = query_name

    # Remove any trailing dots
    encoded = encoded.rstrip('.')

    return encoded


def main():
    parser = argparse.ArgumentParser(
        description="DNS Covert Channel Decoder - Decode hidden messages from DNS queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decode a base32 encoded message
  python decode.py --channel base32 --encoded "jbswy3dpeblw64tmmq"

  # Decode from a full DNS query name
  python decode.py --channel base32 --query "jbswy3dpeblw64tmmq.example.com" --domain "example.com"

  # Decode XOR encrypted message with key
  python decode.py --channel xor --encoded "mruxm3djmzrdgzjsmq" --key "MySecretKey"

  # Decode hex encoded message
  python decode.py --channel hex --encoded "48656c6c6f"

  # Decode TTL values (format: "TTL:72,105" or "72,105")
  python decode.py --channel ttl --encoded "TTL:72,105"
  python decode.py --channel ttl --encoded "72,105"

  # Interactive mode
  python decode.py --channel base32 --interactive
        """
    )

    parser.add_argument(
        '--channel',
        type=str,
        choices=list(CHANNELS.keys()),
        required=True,
        help='Covert channel used for encoding'
    )

    parser.add_argument(
        '--encoded',
        type=str,
        help='Encoded data to decode (just the encoded part, no domain)'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Full DNS query name (e.g., "encoded.example.com")'
    )

    parser.add_argument(
        '--domain',
        type=str,
        default='example.com',
        help='Base domain to strip from query name (default: example.com)'
    )

    parser.add_argument(
        '--key',
        type=str,
        help='Decryption key for channels that support it (e.g., XOR)'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '--output',
        type=str,
        choices=['text', 'hex', 'raw'],
        default='text',
        help='Output format: text (UTF-8), hex, or raw bytes (default: text)'
    )

    args = parser.parse_args()

    # Create channel configuration
    config = {}
    if args.key:
        config['key'] = args.key

    # Interactive mode
    if args.interactive:
        print("\n" + "="*70)
        print("DNS COVERT CHANNEL - INTERACTIVE DECODER")
        print("="*70)
        print(f"Channel: {args.channel}")
        if args.key:
            print(f"Key: {args.key}")
        print("="*70)

        while True:
            try:
                encoded_input = input("\nEnter encoded data (or 'quit' to exit): ").strip()

                if encoded_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if not encoded_input:
                    continue

                # Check if it looks like a full query name
                if '.' in encoded_input and not encoded_input.startswith('.'):
                    domain = input(f"Domain to strip (default: {args.domain}): ").strip() or args.domain
                    encoded_data = extract_encoded_from_query(encoded_input, domain)
                    print(f"Extracted encoded part: {encoded_data}")
                else:
                    encoded_data = encoded_input

                # Decode
                decoded = decode_message(args.channel, encoded_data, config)

                # Display results
                print("\n" + "-"*70)
                print("DECODED MESSAGE:")
                print("-"*70)

                try:
                    print(f"Text: {decoded.decode('utf-8')}")
                except UnicodeDecodeError:
                    print(f"Text: (not valid UTF-8)")

                print(f"Hex:  {decoded.hex()}")
                print(f"Bytes: {decoded}")
                print("-"*70)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n[!] Error: {e}")

        return

    # Non-interactive mode
    if not args.encoded and not args.query:
        parser.error("Either --encoded or --query is required (or use --interactive)")

    # Determine encoded data
    if args.query:
        encoded_data = extract_encoded_from_query(args.query, args.domain)
        print(f"[*] Full query: {args.query}")
        print(f"[*] Extracted encoded part: {encoded_data}")
    else:
        encoded_data = args.encoded
        print(f"[*] Encoded data: {encoded_data}")

    # Decode
    print(f"[*] Using channel: {args.channel}")
    if args.key:
        print(f"[*] Using key: {args.key}")

    decoded = decode_message(args.channel, encoded_data, config)

    # Output based on format
    print("\n" + "="*70)
    print("DECODED MESSAGE")
    print("="*70)

    if args.output == 'text':
        try:
            text = decoded.decode('utf-8')
            print(f"\n{text}\n")
        except UnicodeDecodeError:
            print("\n[!] Cannot decode as UTF-8 text, showing hex instead:")
            print(f"\n{decoded.hex()}\n")

    elif args.output == 'hex':
        print(f"\n{decoded.hex()}\n")

    elif args.output == 'raw':
        # Output raw bytes to stdout
        sys.stdout.buffer.write(decoded)
        return

    print("="*70)

    # Show additional info
    print(f"\nDecoded {len(decoded)} bytes")
    print(f"  Text (UTF-8): {decoded.decode('utf-8', errors='replace')}")
    print(f"  Hex: {decoded.hex()}")
    print(f"  Bytes: {decoded}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
