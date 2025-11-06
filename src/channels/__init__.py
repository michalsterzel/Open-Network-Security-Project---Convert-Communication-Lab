"""
DNS Covert Channel Implementations.

To add a new covert channel:
1. Create a new file in this directory (e.g., my_channel.py)
2. Import CovertChannel from covert_channel_base
3. Create a class that inherits from CovertChannel
4. Implement encode() and decode() methods
5. Import your channel here for easy access
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from channels.base32_channel import Base32Channel
from channels.hex_channel import HexChannel
from channels.xor_base32_channel import XORBase32Channel
from channels.ttl_channel import TTLChannel
from channels.ttl_dns_channel import TTLDNSChannel
from channels.qtype_channel import QTypeChannel
from channels.case_toggle_channel import CaseToggleChannel
from channels.label_count_channel import LabelCountChannel
from channels.txid_channel import TXIDChannel
from channels.rd_flag_channel import RDFlagChannel
from channels.base32_channel_exercise import Base32ChannelExercise

__all__ = [
    'Base32Channel',
    'HexChannel',
    'XORBase32Channel',
    'TTLChannel',
    'TTLDNSChannel',
    'QTypeChannel',
    'CaseToggleChannel',
    'LabelCountChannel',
    'TXIDChannel',
    'RDFlagChannel',
]
