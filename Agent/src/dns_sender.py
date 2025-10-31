"""
DNS Query Sender with print and send modes.
Uses dnspython for DNS operations.
Uses Scapy for TTL covert channel (requires root/sudo).
"""

import dns.message
import dns.query
import socket
from typing import Optional
from dns_packet_builder import DNSPacketBuilder

# Try to import Scapy for TTL support
try:
    from scapy.all import send, sr1, IP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    send = sr1 = IP = None


class DNSSender:
    """
    Utility class for sending or displaying DNS queries.
    Supports both print-only and send modes.
    No root/sudo privileges required!
    """

    def __init__(self, packet_builder: DNSPacketBuilder):
        """
        Initialize DNS sender.

        Args:
            packet_builder: DNSPacketBuilder instance to use
        """
        self.packet_builder = packet_builder

    def print_query(self, query: dns.message.Message, verbose: bool = True):
        """
        Print DNS query information to console.

        Args:
            query: DNS query message to print
            verbose: If True, show full query details
        """
        print("\n" + "="*70)
        print("DNS QUERY INFORMATION")
        print("="*70)

        # Get query info from builder
        info = self.packet_builder.get_query_info(query)

        print(f"\nCovert Channel: {info.get('covert_channel', 'N/A')}")
        print(f"DNS Server: {info.get('dns_server', 'N/A')}:{info.get('port', 53)}")
        print(f"Timeout: {info.get('timeout', 'N/A')}s")

        print(f"\nQuery Name: {info.get('query_name', 'N/A')}")
        print(f"Query Type: {info.get('query_type', 'N/A')}")
        print(f"Query Class: {info.get('query_class', 'N/A')}")
        print(f"Query ID: {info.get('query_id', 'N/A')}")
        print(f"Recursion Desired: {info.get('recursion_desired', 'N/A')}")

        if verbose:
            print("\n" + "-"*70)
            print("FULL QUERY MESSAGE:")
            print("-"*70)
            print(query)

        print("="*70 + "\n")

    def print_response(self, response: dns.message.Message, verbose: bool = True):
        """
        Print DNS response information to console.

        Args:
            response: DNS response message to print
            verbose: If True, show full response details
        """
        print("\n" + "="*70)
        print("DNS RESPONSE INFORMATION")
        print("="*70)

        # Get response info from builder
        info = self.packet_builder.get_response_info(response)

        print(f"\nResponse ID: {info.get('response_id', 'N/A')}")
        print(f"Response Code: {info.get('rcode', 'N/A')}")
        print(f"Answer Count: {info.get('answer_count', 0)}")
        print(f"Authority Count: {info.get('authority_count', 0)}")
        print(f"Additional Count: {info.get('additional_count', 0)}")

        # Print answers if any
        if 'answers' in info and info['answers']:
            print("\nAnswers:")
            for ans in info['answers']:
                print(f"  {ans['name']} {ans['ttl']}s {ans['type']} {ans['data']}")

        if verbose:
            print("\n" + "-"*70)
            print("FULL RESPONSE MESSAGE:")
            print("-"*70)
            print(response)

        print("="*70 + "\n")

    def send_query(
        self,
        query: dns.message.Message,
        use_tcp: bool = False,
        verbose: bool = False
    ) -> Optional[dns.message.Message]:
        """
        Send a DNS query over the network.

        Args:
            query: DNS query message to send
            use_tcp: If True, use TCP instead of UDP
            verbose: Print verbose output during sending

        Returns:
            DNS response message if successful, None otherwise
        """
        try:
            print("\n[*] Sending DNS query...")

            if verbose:
                print(f"[*] DNS Server: {self.packet_builder.dns_server}:{self.packet_builder.port}")
                print(f"[*] Protocol: {'TCP' if use_tcp else 'UDP'}")
                print(f"[*] Timeout: {self.packet_builder.timeout}s")

            # Send query using appropriate protocol
            if use_tcp:
                response = dns.query.tcp(
                    query,
                    self.packet_builder.dns_server,
                    timeout=self.packet_builder.timeout,
                    port=self.packet_builder.port
                )
            else:
                response = dns.query.udp(
                    query,
                    self.packet_builder.dns_server,
                    timeout=self.packet_builder.timeout,
                    port=self.packet_builder.port
                )

            print("[+] Query sent successfully!")
            print(f"[+] Response received (ID: {response.id})")

            return response

        except dns.exception.Timeout:
            print("[-] DNS query timed out (no response received)")
            return None
        except socket.error as e:
            print(f"\n[!] Socket error: {e}")
            return None
        except Exception as e:
            print(f"\n[!] ERROR sending query: {e}")
            return None

    def print_and_send(
        self,
        query: dns.message.Message,
        use_tcp: bool = False,
        verbose_query: bool = True,
        verbose_response: bool = True,
        verbose_send: bool = False
    ) -> Optional[dns.message.Message]:
        """
        Print query information and then send it.

        Args:
            query: DNS query message
            use_tcp: Use TCP instead of UDP
            verbose_query: Show full query details when printing
            verbose_response: Show full response details when printing
            verbose_send: Show verbose output when sending

        Returns:
            DNS response if successful, else None
        """
        self.print_query(query, verbose=verbose_query)
        response = self.send_query(query, use_tcp=use_tcp, verbose=verbose_send)

        if response:
            self.print_response(response, verbose=verbose_response)

        return response

    def process_queries(
        self,
        queries: list,
        mode: str = "print",
        use_tcp: bool = False,
        delay: float = 0.0
    ):
        """
        Process multiple DNS queries with specified mode.

        Args:
            queries: List of DNS query messages
            mode: "print", "send", or "both"
            use_tcp: Use TCP instead of UDP
            delay: Delay between queries in seconds
        """
        import time

        responses = []

        for i, query in enumerate(queries, 1):
            print(f"\n{'='*70}")
            print(f"QUERY {i}/{len(queries)}")
            print(f"{'='*70}")

            if mode == "print":
                self.print_query(query, verbose=True)
            elif mode == "send":
                response = self.send_query(query, use_tcp=use_tcp)
                responses.append(response)
                if response:
                    self.print_response(response, verbose=False)
            elif mode == "both":
                response = self.print_and_send(query, use_tcp=use_tcp)
                responses.append(response)
            else:
                print(f"[!] Unknown mode: {mode}")
                continue

            if delay > 0 and i < len(queries):
                print(f"\n[*] Waiting {delay}s before next query...")
                time.sleep(delay)

        if mode in ["send", "both"]:
            print(f"\n[*] Sent {len(queries)} queries, received {sum(1 for r in responses if r)} responses")
            return responses

    def print_ttl_queries(self, queries_with_ttl: list, verbose: bool = True):
        """
        Print information about TTL-based queries.

        Args:
            queries_with_ttl: List of (query, ttl_value) tuples
            verbose: If True, show full details
        """
        print("\n" + "="*70)
        print("DNS TTL COVERT CHANNEL - QUERIES")
        print("="*70)

        # Get info from builder
        info = self.packet_builder.get_ttl_queries_info(queries_with_ttl)

        print(f"\nCovert Channel: {info.get('covert_channel', 'N/A')}")
        print(f"DNS Server: {info.get('dns_server', 'N/A')}")
        print(f"Total Queries: {info.get('total_queries', 0)}")
        print(f"Scapy Available: {info.get('scapy_available', False)}")

        if info.get('scapy_available'):
            print("\n[+] Using Scapy for raw socket control")
            print("    TTL values will be set in IP packets")
            print("    Requires root/sudo privileges to send")
        else:
            print("\n[!] Scapy not available")
            print("    Cannot set IP-level TTL")
            print("    Install with: pip install scapy")

        print("\n" + "-"*70)
        print("QUERY SEQUENCE:")
        print("-"*70)

        for query_info in info.get('queries', []):
            print(f"\nQuery #{query_info['sequence']}:")
            print(f"  Query Name: {query_info.get('query_name', 'N/A')}")
            print(f"  Query Type: {query_info.get('query_type', 'N/A')}")
            print(f"  TTL Value:  {query_info['ttl_value']} (dec) = {query_info['ttl_hex']} (hex)")
            print(f"  As char:    '{query_info['ttl_char']}'")

        if verbose and len(queries_with_ttl) > 0:
            print("\n" + "-"*70)
            print("FULL QUERY DETAILS (First Query):")
            print("-"*70)
            print(queries_with_ttl[0][0])  # Print first query

        print("="*70 + "\n")

    def send_ttl_queries(
        self,
        queries_with_ttl: list,
        use_tcp: bool = False,
        delay: float = 0.1,
        verbose: bool = False,
        wait_for_response: bool = False
    ) -> list:
        """
        Send TTL-based queries sequentially using Scapy (if available).

        Uses Scapy for raw socket access to properly set IP-level TTL.
        Requires root/sudo privileges.

        Args:
            queries_with_ttl: List of (packet, ttl_value) tuples
            use_tcp: Use TCP instead of UDP (ignored for Scapy)
            delay: Delay between queries in seconds
            verbose: Print verbose output
            wait_for_response: Wait for DNS responses

        Returns:
            List of response packets/messages
        """
        import time
        import os

        print(f"\n[*] Sending {len(queries_with_ttl)} TTL-encoded queries...")
        print(f"[*] Delay between queries: {delay}s")

        # Check if using Scapy packets
        if SCAPY_AVAILABLE and len(queries_with_ttl) > 0 and hasattr(queries_with_ttl[0][0], 'haslayer'):
            # Using Scapy - proper TTL control!
            print(f"[+] Using Scapy with custom TTL values")

            # Check for root privileges
            if os.geteuid() != 0:
                print(f"\n[!] ERROR: Scapy requires root/sudo privileges")
                print(f"[!] Run with: sudo python main.py ...")
                return []

            responses = []

            for i, (packet, ttl) in enumerate(queries_with_ttl, 1):
                if verbose:
                    print(f"\n[*] Query {i}/{len(queries_with_ttl)}: TTL={ttl}")
                    if packet.haslayer(IP):
                        print(f"    IP TTL: {packet[IP].ttl}")

                try:
                    if wait_for_response:
                        # Send and receive
                        response = sr1(
                            packet,
                            timeout=self.packet_builder.timeout,
                            verbose=0
                        )
                        responses.append(response)

                        if verbose:
                            if response:
                                print(f"[+] Response received")
                            else:
                                print(f"[-] No response (timeout)")
                    else:
                        # Send only
                        send(packet, verbose=0)
                        responses.append(None)

                        if verbose:
                            print(f"[+] Packet sent")

                except PermissionError:
                    print(f"\n[!] ERROR: Permission denied - run with sudo")
                    return responses
                except Exception as e:
                    responses.append(None)
                    if verbose:
                        print(f"[!] Error: {e}")

                # Delay before next query
                if i < len(queries_with_ttl) and delay > 0:
                    time.sleep(delay)

            successful = sum(1 for r in responses if r is not None)
            print(f"\n[+] Sent {len(queries_with_ttl)} queries with custom TTL values")
            if wait_for_response:
                print(f"[*] Received {successful} responses")

            return responses

        else:
            # Scapy not available or not Scapy packets
            print(f"\n[!] WARNING: Cannot set IP-level TTL")
            print(f"[!] Scapy not available or not installed")
            print(f"[!] Install with: pip install scapy")
            print(f"[!] TTL values will NOT be encoded in packets")

            return []
