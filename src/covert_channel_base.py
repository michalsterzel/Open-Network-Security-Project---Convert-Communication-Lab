"""
Abstract base class for DNS covert channels.
To create a new covert channel, inherit from CovertChannel and implement
the encode() and decode() methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class CovertChannel(ABC):
    """
    Abstract base class for implementing DNS covert channels.

    Each covert channel must implement encoding and decoding methods
    that transform data into DNS-compatible formats and back.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the covert channel.

        Args:
            config: Optional configuration dictionary for the channel
        """
        self.config = config or {}

    @abstractmethod
    def encode(self, data: bytes) -> str:
        """
        Encode data into a DNS-compatible format (e.g., subdomain, TXT record).

        Args:
            data: Raw bytes to encode

        Returns:
            Encoded string suitable for DNS packet
        """
        pass

    @abstractmethod
    def decode(self, encoded_data: str) -> bytes:
        """
        Decode DNS data back to original bytes.

        Args:
            encoded_data: DNS-encoded string

        Returns:
            Original raw bytes
        """
        pass

    @property
    def name(self) -> str:
        """Return the name of this covert channel implementation."""
        return self.__class__.__name__

    def get_description(self) -> str:
        """Return a description of this covert channel."""
        return self.__doc__ or "No description available"
