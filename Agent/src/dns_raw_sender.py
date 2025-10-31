"""
Raw Socket DNS Sender for TTL Covert Channel

This module uses Scapy to send DNS queries with custom IP-level TTL values.
Requires root/sudo privileges for raw socket access.
"""

from scapy.all import IP, UDP, DNS, DNSQR, sr1, send
from typing import Optional, List, Tuple
import time


class RawDNSSender:
    """
    DNS sender using raw sockets (Scapy) with full TTL control.

    This is required for TTL covert channels where we need to set
    the IP-level Time-To-Live field to encode data.
    """

    def __init__(
        self,
        dns_server: str = "8.8.8.8",
        source_ip: Optional[str] = None,
        source_port: int = 53000,
        dest_port: int = 53,
        timeout: int = 2
    ):
        """
        Initialize raw DNS sender.

        Args:
            dns_server: Destination DNS server IP
            source_ip: Source IP (None for auto)
            source_port: Source UDP port
            dest_port: Destination UDP port (53 for DNS)
            timeout: Response timeout in seconds
        """
        self.dns_server = dns_server
        self.source_ip = source_ip
        self.source_port = source_port
        self.dest_port = dest_port
        self.timeout = timeout

    def build_dns_packet(
        self,
        query_name: str,
        ttl_value: int,
        qtype: str = "A"
    ) -> IP:
        """
        Build a DNS query packet with custom TTL.

        Args:
            query_name: DNS query name (e.g., "example.com")
            ttl_value: IP-level TTL value (1-255)
            qtype: DNS query type (A, AAAA, TXT, etc.)

        Returns:
            Scapy IP packet with DNS query and custom TTL
        """
        # Ensure TTL is in valid range
        if not 1 <= ttl_value <= 255:
            raise ValueError(f"TTL must be between 1 and 255, got {ttl_value}")

        # Build DNS query layer
        dns_layer = DNS(
            rd=1,  # Recursion desired
            qd=DNSQR(qname=query_name, qtype=qtype)
        )

        # Build IP layer with custom TTL
        if self.source_ip:
            ip_layer = IP(
                src=self.source_ip,
                dst=self.dns_server,
                ttl=ttl_value  # THIS is where we set the custom TTL!
            )
        else:
            ip_layer = IP(
                dst=self.dns_server,
                ttl=ttl_value  # THIS is where we set the custom TTL!
            )

        # Build UDP layer
        udp_layer = UDP(
            sport=self.source_port,
            dport=self.dest_port
        )

        # Combine layers
        packet = ip_layer / udp_layer / dns_layer

        return packet

    def send_packet(
        self,
        packet: IP,
        wait_for_response: bool = False,
        verbose: bool = False
    ) -> Optional[IP]:
        """
        Send a DNS packet with custom TTL.

        Args:
            packet: Scapy IP packet to send
            wait_for_response: Wait for DNS response
            verbose: Print verbose Scapy output

        Returns:
            Response packet if wait_for_response=True, else None
        """
        try:
            if wait_for_response:
                # Send and receive
                response = sr1(
                    packet,
                    timeout=self.timeout,
                    verbose=verbose
                )
                return response
            else:
                # Send only
                send(packet, verbose=verbose)
                return None

        except PermissionError:
            raise PermissionError(
                "Raw socket access requires root/sudo privileges. "
                "Run with: sudo python main.py ..."
            )
        except Exception as e:
            raise RuntimeError(f"Error sending packet: {e}")

    def send_ttl_query(
        self,
        query_name: str,
        ttl_value: int,
        qtype: str = "A",
        wait_for_response: bool = False,
        verbose: bool = False
    ) -> Optional[IP]:
        """
        Build and send a DNS query with custom TTL.

        Args:
            query_name: DNS query name
            ttl_value: IP TTL value (1-255)
            qtype: DNS query type
            wait_for_response: Wait for response
            verbose: Verbose output

        Returns:
            Response packet if requested, else None
        """
        packet = self.build_dns_packet(query_name, ttl_value, qtype)
        return self.send_packet(packet, wait_for_response, verbose)

    def send_ttl_sequence(
        self,
        queries_with_ttl: List[Tuple[str, int]],
        qtype: str = "A",
        delay: float = 0.1,
        wait_for_responses: bool = False,
        verbose: bool = False
    ) -> List[Optional[IP]]:
        """
        Send a sequence of DNS queries with different TTL values.

        This is the main method for TTL covert channel communication.

        Args:
            queries_with_ttl: List of (query_name, ttl_value) tuples
            qtype: DNS query type
            delay: Delay between queries in seconds
            wait_for_responses: Wait for responses
            verbose: Verbose output

        Returns:
            List of response packets (or None if not waiting)
        """
        responses = []

        for i, (query_name, ttl_value) in enumerate(queries_with_ttl):
            if verbose:
                print(f"[*] Query {i+1}/{len(queries_with_ttl)}: "
                      f"{query_name} with TTL={ttl_value}")

            try:
                response = self.send_ttl_query(
                    query_name,
                    ttl_value,
                    qtype,
                    wait_for_responses,
                    verbose=False
                )
                responses.append(response)

                if verbose and response:
                    print(f"[+] Response received")

            except Exception as e:
                if verbose:
                    print(f"[!] Error: {e}")
                responses.append(None)

            # Delay before next query
            if i < len(queries_with_ttl) - 1 and delay > 0:
                time.sleep(delay)

        return responses

    def print_packet_info(self, packet: IP, show_layers: bool = True):
        """
        Print information about a packet.

        Args:
            packet: Scapy packet
            show_layers: Show detailed layer information
        """
        print("\n" + "="*70)
        print("PACKET INFORMATION")
        print("="*70)

        if IP in packet:
            print(f"\nIP Layer:")
            print(f"  Source IP: {packet[IP].src}")
            print(f"  Dest IP: {packet[IP].dst}")
            print(f"  TTL: {packet[IP].ttl} (0x{packet[IP].ttl:02x})")
            print(f"  Protocol: {packet[IP].proto}")

        if UDP in packet:
            print(f"\nUDP Layer:")
            print(f"  Source Port: {packet[UDP].sport}")
            print(f"  Dest Port: {packet[UDP].dport}")

        if DNS in packet:
            dns_layer = packet[DNS]
            print(f"\nDNS Layer:")
            print(f"  Query ID: {dns_layer.id}")
            print(f"  Recursion Desired: {bool(dns_layer.rd)}")

            if dns_layer.qd:
                print(f"  Query Name: {dns_layer.qd.qname.decode() if isinstance(dns_layer.qd.qname, bytes) else dns_layer.qd.qname}")
                print(f"  Query Type: {dns_layer.qd.qtype}")

        if show_layers:
            print("\n" + "-"*70)
            print("FULL PACKET:")
            print("-"*70)
            packet.show()

        print("="*70 + "\n")


def check_scapy_available():
    """Check if Scapy is available and can be used."""
    try:
        from scapy.all import IP
        return True
    except ImportError:
        return False


def check_root_privileges():
    """Check if running with root/sudo privileges."""
    import os
    return os.geteuid() == 0
