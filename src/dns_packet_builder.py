"""
DNS Query Builder for creating DNS queries with covert channels.
Uses dnspython for simplified DNS operations.
Uses Scapy for TTL-based covert channels (requires raw sockets).
"""

import dns.message
import dns.query
import dns.rdatatype
from typing import Optional, List, Tuple, Union
from covert_channel_base import CovertChannel

# Try to import Scapy for TTL support
try:
    from scapy.all import IP, UDP, DNS, DNSQR
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    IP = UDP = DNS = DNSQR = None


class DNSPacketBuilder:
    """
    Builder class for creating DNS queries with embedded covert channel data.
    Uses dnspython library for clean, high-level DNS operations.
    """

    def __init__(
        self,
        covert_channel: CovertChannel,
        dns_server: str = "8.8.8.8",
        timeout: float = 2.0,
        port: int = 53
    ):
        """
        Initialize DNS query builder.

        Args:
            covert_channel: CovertChannel implementation to use
            dns_server: Destination DNS server IP
            timeout: Query timeout in seconds
            port: DNS server port (default: 53)
        """
        self.covert_channel = covert_channel
        self.dns_server = dns_server
        self.timeout = timeout
        self.port = port

    def build_query(
        self,
        data: bytes,
        domain: str = "example.com",
        qtype: str = "A"
    ) -> dns.message.Message:
        """
        Build a DNS query message with encoded covert data.

        Args:
            data: Raw data to encode in the DNS query
            domain: Base domain name
            qtype: DNS query type (A, AAAA, TXT, etc.)

        Returns:
            DNS query message object
        """
        # Encode data using the covert channel
        encoded_data = self.covert_channel.encode(data)

        # Construct the full DNS query name
        # The encoded data becomes part of the subdomain
        query_name = f"{encoded_data}.{domain}"

        # Create DNS query message
        query = dns.message.make_query(
            qname=query_name,
            rdtype=qtype,
            rdclass='IN'
        )

        return query

    def build_txt_query(
        self,
        data: bytes,
        domain: str = "example.com",
        subdomain: Optional[str] = None
    ) -> dns.message.Message:
        """
        Build a DNS TXT record query with encoded data.

        Args:
            data: Raw data to encode
            domain: Base domain name
            subdomain: Optional subdomain prefix

        Returns:
            DNS query message object
        """
        encoded_data = self.covert_channel.encode(data)

        # For TXT queries, we can embed data in the subdomain
        if subdomain:
            query_name = f"{subdomain}.{encoded_data}.{domain}"
        else:
            query_name = f"{encoded_data}.{domain}"

        # Create TXT query
        query = dns.message.make_query(
            qname=query_name,
            rdtype='TXT',
            rdclass='IN'
        )

        return query

    def get_query_info(self, query: dns.message.Message) -> dict:
        """
        Extract information from a DNS query for display.

        Args:
            query: DNS query message

        Returns:
            Dictionary with query information
        """
        info = {
            "covert_channel": self.covert_channel.name,
            "dns_server": self.dns_server,
            "port": self.port,
            "timeout": self.timeout,
        }

        # Extract query details
        if query.question:
            question = query.question[0]
            info["query_name"] = str(question.name)
            info["query_type"] = dns.rdatatype.to_text(question.rdtype)
            info["query_class"] = dns.rdataclass.to_text(question.rdclass)

        # Query metadata
        info["query_id"] = query.id
        info["flags"] = query.flags
        info["recursion_desired"] = bool(query.flags & dns.flags.RD)

        return info

    def get_response_info(self, response: dns.message.Message) -> dict:
        """
        Extract information from a DNS response for display.

        Args:
            response: DNS response message

        Returns:
            Dictionary with response information
        """
        info = {
            "response_id": response.id,
            "flags": response.flags,
            "rcode": dns.rcode.to_text(response.rcode()),
            "answer_count": len(response.answer),
            "authority_count": len(response.authority),
            "additional_count": len(response.additional),
        }

        # Extract answer records
        if response.answer:
            info["answers"] = []
            for rrset in response.answer:
                for rdata in rrset:
                    info["answers"].append({
                        "name": str(rrset.name),
                        "type": dns.rdatatype.to_text(rrset.rdtype),
                        "ttl": rrset.ttl,
                        "data": str(rdata)
                    })

        return info

    def build_ttl_queries(
        self,
        data: bytes,
        domain: str = "example.com",
        qtype: str = "A",
        base_subdomain: str = "query",
        source_ip: Optional[str] = None,
        source_port: int = 53000
    ) -> List[Tuple[Union['IP', str], int]]:
        """
        Build multiple DNS queries for TTL-based covert channel using Scapy.

        For TTL channels, each byte requires a separate query.
        Returns list of (scapy_packet, ttl_value) tuples.

        REQUIRES: Scapy library and root/sudo privileges to send.

        Args:
            data: Raw data to encode
            domain: Base domain name
            qtype: DNS query type
            base_subdomain: Base subdomain for queries
            source_ip: Source IP address (None for auto)
            source_port: Source UDP port

        Returns:
            List of (IP_packet, ttl_value) tuples if Scapy available,
            otherwise List of (query_name, ttl_value) tuples
        """
        # Check if this is a TTL channel
        if not hasattr(self.covert_channel, 'get_ttl_values'):
            raise ValueError("Current channel does not support TTL encoding")

        # Get TTL values from the channel
        ttl_values = self.covert_channel.get_ttl_values(data)

        queries = []

        if SCAPY_AVAILABLE:
            # Build Scapy packets with custom TTL
            for i, ttl_value in enumerate(ttl_values):
                # Create unique subdomain for each query
                query_name = f"{base_subdomain}{i+1}.{domain}"

                # Build DNS layer
                dns_layer = DNS(
                    rd=1,  # Recursion desired
                    qd=DNSQR(qname=query_name, qtype=qtype)
                )

                # Build IP layer with custom TTL
                if source_ip:
                    ip_layer = IP(
                        src=source_ip,
                        dst=self.dns_server,
                        ttl=ttl_value  # Set custom TTL here!
                    )
                else:
                    ip_layer = IP(
                        dst=self.dns_server,
                        ttl=ttl_value  # Set custom TTL here!
                    )

                # Build UDP layer
                udp_layer = UDP(sport=source_port, dport=53)

                # Combine layers
                packet = ip_layer / udp_layer / dns_layer

                queries.append((packet, ttl_value))
        else:
            # Scapy not available, return query names with TTL values
            for i, ttl_value in enumerate(ttl_values):
                query_name = f"{base_subdomain}{i+1}.{domain}"
                queries.append((query_name, ttl_value))

        return queries

    def get_ttl_queries_info(
        self,
        queries: List[Tuple[Union['IP', str], int]]
    ) -> dict:
        """
        Get information about TTL-based queries.

        Args:
            queries: List of (packet_or_name, ttl_value) tuples

        Returns:
            Dictionary with queries information
        """
        info = {
            "covert_channel": self.covert_channel.name,
            "dns_server": self.dns_server,
            "total_queries": len(queries),
            "scapy_available": SCAPY_AVAILABLE,
            "queries": []
        }

        for i, (query, ttl) in enumerate(queries, 1):
            query_info = {
                "sequence": i,
                "ttl_value": ttl,
                "ttl_hex": f"0x{ttl:02x}",
                "ttl_char": chr(ttl) if 32 <= ttl < 127 else f"\\x{ttl:02x}",
            }

            # Handle Scapy packets
            if SCAPY_AVAILABLE and hasattr(query, 'haslayer'):
                if query.haslayer(DNS):
                    dns_layer = query[DNS]
                    if dns_layer.qd:
                        query_info["query_name"] = dns_layer.qd.qname.decode() if isinstance(dns_layer.qd.qname, bytes) else str(dns_layer.qd.qname)
                        query_info["query_type"] = dns_layer.qd.qtype

                if query.haslayer(IP):
                    query_info["ip_ttl"] = query[IP].ttl
            # Handle query names (when Scapy not available)
            elif isinstance(query, str):
                query_info["query_name"] = query
                query_info["query_type"] = "A"

            info["queries"].append(query_info)

        return info
