import sys
from zlib import crc32


PACKET_DELIMITER = ' '.encode()

def verify_checksum(packet: bytes) -> bool:
    packet_length = len(packet)
    index = 0
    packet_checksum = b''

    while index < packet_length:
        curr = packet[index].to_bytes(1, sys.byteorder)
        index += 1
        if curr != PACKET_DELIMITER:
            packet_checksum += curr
        else:
            break
    
    packet_data = packet[index:]
    checksum = crc32(packet_data).to_bytes(4, sys.byteorder)
    return packet_checksum == checksum

def extract_data(packet: bytes) -> bytes:
    packet_length = len(packet)
    index = 0

    while index < packet_length:
        curr = packet[index].to_bytes(1, sys.byteorder)
        index += 1
        if curr == PACKET_DELIMITER:
            break
    
    return packet[index:]
