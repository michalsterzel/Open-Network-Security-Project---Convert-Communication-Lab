#!/usr/bin/env python3
"""
DNS Covert Channel - Main Script

Usage:
    python main.py --channel base32 --data "secret message" --mode print
    python main.py --channel xor --data "secret message" --mode send --dns-server 8.8.8.8
    python main.py --channel hex --data "test" --mode both --domain example.com
"""

import argparse
import sys
from typing import Optional

# Import covert channel implementations
from channels import Base32Channel, HexChannel, XORBase32Channel, TTLChannel
from dns_packet_builder import DNSPacketBuilder
from dns_sender import DNSSender


# Available covert channels
CHANNELS = {
    'base32': Base32Channel,
    'hex': HexChannel,
    'xor': XORBase32Channel,
    'ttl': TTLChannel,
}


def list_channels():
    """List all available covert channels."""
    print("\nAvailable Covert Channels:")
    print("=" * 70)
    for name, channel_class in CHANNELS.items():
        instance = channel_class()
        print(f"\n{name}:")
        print(f"  {instance.get_description()}")
    print("=" * 70 + "\n")


def create_channel(channel_name: str, config: Optional[dict] = None):
    """
    Create a covert channel instance.

    Args:
        channel_name: Name of the channel
        config: Optional configuration dict

    Returns:
        CovertChannel instance
    """
    if channel_name not in CHANNELS:
        print(f"[!] Error: Unknown channel '{channel_name}'")
        print(f"[*] Available channels: {', '.join(CHANNELS.keys())}")
        sys.exit(1)

    channel_class = CHANNELS[channel_name]
    return channel_class(config)


def main():
    parser = argparse.ArgumentParser(
        description="DNS Covert Channel Tool - Send data hidden in DNS packets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print query only (no sending)
  python main.py --channel base32 --data "Hello World" --mode print

  # Send query to DNS server (no sudo required!)
  python main.py --channel xor --data "secret" --mode send --dns-server 8.8.8.8

  # Print and send query
  python main.py --channel hex --data "test123" --mode both --domain example.com

  # Use custom XOR key
  python main.py --channel xor --data "secret" --key "MyKey" --mode print

  # List all available channels
  python main.py --list-channels
        """
    )

    parser.add_argument(
        '--list-channels',
        action='store_true',
        help='List all available covert channels'
    )

    parser.add_argument(
        '--channel',
        type=str,
        choices=list(CHANNELS.keys()),
        help='Covert channel to use'
    )

    parser.add_argument(
        '--data',
        type=str,
        help='Data to encode and send'
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['print', 'send', 'both'],
        default='print',
        help='Mode: print (show only), send (send only), or both (default: print)'
    )

    parser.add_argument(
        '--dns-server',
        type=str,
        default='8.8.8.8',
        help='DNS server IP address (default: 8.8.8.8)'
    )

    parser.add_argument(
        '--domain',
        type=str,
        default='example.com',
        help='Base domain for DNS query (default: example.com)'
    )

    parser.add_argument(
        '--qtype',
        type=str,
        default='A',
        help='DNS query type: A, AAAA, TXT, etc. (default: A)'
    )

    parser.add_argument(
        '--key',
        type=str,
        help='Encryption key for channels that support it (e.g., XOR)'
    )

    parser.add_argument(
        '--wait-response',
        action='store_true',
        help='Wait for DNS response when sending'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=2,
        help='Response timeout in seconds (default: 2)'
    )

    parser.add_argument(
        '--use-tcp',
        action='store_true',
        help='Use TCP instead of UDP for DNS queries'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show verbose query details'
    )

    args = parser.parse_args()

    # Handle list channels
    if args.list_channels:
        list_channels()
        return

    # Validate required arguments
    if not args.channel:
        parser.error("--channel is required (use --list-channels to see available channels)")

    if not args.data:
        parser.error("--data is required")

    # Create channel configuration
    config = {}
    if args.key:
        config['key'] = args.key

    # Create covert channel
    print(f"[*] Using covert channel: {args.channel}")
    channel = create_channel(args.channel, config)

    # Create query builder
    builder = DNSPacketBuilder(
        covert_channel=channel,
        dns_server=args.dns_server,
        timeout=args.timeout
    )

    # Create sender
    sender = DNSSender(builder)

    # Convert data to bytes
    data_bytes = args.data.encode('utf-8')
    print(f"[*] Original data: {args.data}")
    print(f"[*] Data size: {len(data_bytes)} bytes")

    # Check if using TTL channel (requires special handling)
    if args.channel == 'ttl':
        print(f"[*] Building DNS queries for TTL channel...")
        print(f"[!] TTL channel requires {len(data_bytes)} queries (1 per byte)")

        # Build TTL queries
        queries_with_ttl = builder.build_ttl_queries(
            data_bytes,
            domain=args.domain,
            qtype=args.qtype
        )

        # Process based on mode
        if args.mode == 'print':
            sender.print_ttl_queries(queries_with_ttl, verbose=args.verbose)

        elif args.mode == 'send':
            sender.print_ttl_queries(queries_with_ttl, verbose=False)
            sender.send_ttl_queries(
                queries_with_ttl,
                use_tcp=args.use_tcp,
                delay=0.1,
                verbose=args.verbose
            )

        elif args.mode == 'both':
            sender.print_ttl_queries(queries_with_ttl, verbose=args.verbose)
            sender.send_ttl_queries(
                queries_with_ttl,
                use_tcp=args.use_tcp,
                delay=0.1,
                verbose=args.verbose
            )

    else:
        # Standard channels (base32, hex, xor)
        print(f"[*] Building DNS query...")
        if args.qtype.upper() == 'TXT':
            query = builder.build_txt_query(data_bytes, domain=args.domain)
        else:
            query = builder.build_query(data_bytes, domain=args.domain, qtype=args.qtype)

        # Process based on mode
        if args.mode == 'print':
            sender.print_query(query, verbose=args.verbose)

        elif args.mode == 'send':
            response = sender.send_query(
                query,
                use_tcp=args.use_tcp,
                verbose=args.verbose
            )
            if response:
                sender.print_response(response, verbose=False)

        elif args.mode == 'both':
            response = sender.print_and_send(
                query,
                use_tcp=args.use_tcp,
                verbose_query=args.verbose,
                verbose_response=args.verbose,
                verbose_send=args.verbose
            )

    print("\n[+] Done!")


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
