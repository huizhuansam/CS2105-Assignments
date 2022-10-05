import sys
from zlib import crc32

PACKET_DELIMITER = ' '.encode()
MAXIMUM_PACKET_SIZE = 64


def generate_packet(line: bytes) -> bytes:
    checksum = crc32(line).to_bytes(4, sys.byteorder)
    return checksum + PACKET_DELIMITER + line
