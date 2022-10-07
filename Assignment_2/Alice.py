# ***** DATA SEGMENT FORMAT *****
# First 4 bytes: checksum of sequence number + application data
# Second 4 bytes: sequence number
# Last 56 bytes: application data

import argparse
import sys
from socket import *
from zlib import crc32

# Command line parsing
def get_server_port() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('server_port_number', type=int)
    args = parser.parse_args()
    return args.server_port_number

# Global constants
MAX_PACKET_BYTES = 64
MAX_CHECKSUM_BYTES = 4
MAX_SEQUENCE_NUMBER_BYTES = 4
MAX_DATA_BYTES = MAX_PACKET_BYTES - MAX_CHECKSUM_BYTES - MAX_SEQUENCE_NUMBER_BYTES
HEADER_PADDING = b'\x00'
CHECKSUM_INDEX_BEGIN = 0
CHECKSUM_INDEX_END = 4
SEQUENCE_NUMBER_INDEX_BEGIN = 4
SEQUENCE_NUMBER_INDEX_END = 8
TIMEOUT_VALUE = 5
LOCALHOST = 'localhost'

def generate_packet(data: bytes, sequence_number: int) -> bytes:
    sequence_bytes = (sequence_number
        .to_bytes(MAX_SEQUENCE_NUMBER_BYTES, sys.byteorder)
        .rjust(MAX_SEQUENCE_NUMBER_BYTES, HEADER_PADDING))
    checksum = (crc32(sequence_bytes + data)
        .to_bytes(MAX_CHECKSUM_BYTES, sys.byteorder)
        .rjust(MAX_CHECKSUM_BYTES, HEADER_PADDING))
    return checksum + sequence_bytes + data

def extract_checksum(acknowledgement: bytes) -> int:
    return int.from_bytes(acknowledgement[CHECKSUM_INDEX_BEGIN : CHECKSUM_INDEX_END], sys.byteorder)

def extract_ack_bytes(acknowledgement: bytes) -> bytes:
    return acknowledgement[SEQUENCE_NUMBER_INDEX_BEGIN : SEQUENCE_NUMBER_INDEX_END]

def extract_ack_number(acknowledgement: bytes) -> int:
    return int.from_bytes(extract_ack_bytes(acknowledgement), sys.byteorder)

def transmit_packet_return_ack(
    alice_socket: socket, 
    server_name: str, 
    server_port: int, 
    packet: bytes, 
    base_sequence_number: int) -> int:
    alice_socket.sendto(packet, (server_name, server_port))
    acknowledgement, server_address = alice_socket.recvfrom(MAX_PACKET_BYTES)
    ack_checksum = extract_checksum(acknowledgement)
    ack_bytes = extract_ack_bytes(acknowledgement)
    if ack_checksum != crc32(ack_bytes):
        return base_sequence_number
    return extract_ack_number(acknowledgement)

def serve(alice_socket: socket, server_name: str, server_port: int) -> None:
    alice_socket.settimeout(TIMEOUT_VALUE)
    reader = sys.stdin.buffer
    sequence_number = 0
    retransmit = False
    data = b''
    # TODO

def run_alice() -> None:
    server_port = get_server_port()
    alice_socket = socket(AF_INET, SOCK_DGRAM)
    serve(alice_socket, LOCALHOST, server_port)
    alice_socket.close()

run_alice()
