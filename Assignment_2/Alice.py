# ***** DATA SEGMENT FORMAT *****
# First 4 bytes: checksum of sequence number + application data
# Second 4 bytes: sequence number
# Last 56 bytes: application data

import argparse
import sys
from socket import *
from typing import Tuple
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
TIMEOUT_VALUE = 0.1
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

def is_acknowledgement_corrupted(acknowledgement: bytes) -> bool:
    ack_checksum = extract_checksum(acknowledgement)
    ack_bytes = extract_ack_bytes(acknowledgement)
    return ack_checksum != crc32(ack_bytes)

def read_and_send(alice_socket: socket, server_address: Tuple[str, int], sequence_number: int) -> bytes:
    reader = sys.stdin.buffer
    data = reader.read1(MAX_DATA_BYTES)
    if len(data) < 1:
        return data
    packet = generate_packet(data, sequence_number)
    alice_socket.sendto(packet, server_address)
    return packet

def wait_ack(alice_socket: socket, expected_sequence_number: int, server_address: Tuple[str, int], packet: bytes) -> int:
    while True:
        alice_socket.settimeout(TIMEOUT_VALUE)
        try:
            acknowledgement, _ = alice_socket.recvfrom(MAX_PACKET_BYTES)
            if (not is_acknowledgement_corrupted(acknowledgement)) and (extract_ack_number(acknowledgement) == expected_sequence_number):
                return abs(expected_sequence_number - 1)
            alice_socket.sendto(packet, server_address)                
        except:
            alice_socket.sendto(packet, server_address)

def serve(alice_socket: socket, server_address: Tuple[str, int]) -> None:
    # RDT3.0 Finite state model
    sequence_number = 0
    while True:
        packet = read_and_send(alice_socket, server_address, sequence_number)
        if len(packet) < 1:
            return
        sequence_number = wait_ack(alice_socket, sequence_number, server_address, packet)

def run_alice() -> None:
    server_port = get_server_port()
    alice_socket = socket(AF_INET, SOCK_DGRAM)
    serve(alice_socket, (LOCALHOST, server_port))
    alice_socket.close()

run_alice()
