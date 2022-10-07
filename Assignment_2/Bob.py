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
LOCALHOST = 'localhost'

def generate_acknowledgement(sequence_number: int) -> bytes:
    sequence_bytes = (sequence_number
        .to_bytes(MAX_SEQUENCE_NUMBER_BYTES, sys.byteorder)
        .rjust(MAX_SEQUENCE_NUMBER_BYTES, HEADER_PADDING))
    checksum = (crc32(sequence_bytes)
        .to_bytes(MAX_CHECKSUM_BYTES, sys.byteorder)
        .rjust(MAX_CHECKSUM_BYTES, HEADER_PADDING))
    return checksum + sequence_bytes

def extract_checksum(packet: bytes) -> int:
    return int.from_bytes(packet[CHECKSUM_INDEX_BEGIN : CHECKSUM_INDEX_END], sys.byteorder)

def extract_sequence_number(packet: bytes) -> int:
    return int.from_bytes(packet[SEQUENCE_NUMBER_INDEX_BEGIN: SEQUENCE_NUMBER_INDEX_END], sys.byteorder)

def extract_data(packet: bytes) -> bytes:
    return packet[SEQUENCE_NUMBER_INDEX_END:]

def is_packet_corrupted(packet: bytes) -> bool:
    packet_checksum = extract_checksum(packet)
    payload_checksum = crc32(packet[SEQUENCE_NUMBER_INDEX_BEGIN:])
    return packet_checksum != payload_checksum

def wait_packet(bob_socket: socket, expected_sequence_number: int) -> int:
    writer = sys.stdout.buffer
    while True:
        packet, client_address = bob_socket.recvfrom(MAX_PACKET_BYTES)
        if is_packet_corrupted(packet) or extract_sequence_number(packet) != expected_sequence_number:
            bob_socket.sendto(generate_acknowledgement(abs(expected_sequence_number - 1)), client_address)
            continue
        data = extract_data(packet)
        writer.write(data)
        writer.flush()
        bob_socket.sendto(generate_acknowledgement(expected_sequence_number), client_address)
        return abs(expected_sequence_number - 1)
            
def serve(bob_socket: socket) -> None:
    # RDT3.0 Finite state model
    expected_sequence_number = 0
    while True:
        expected_sequence_number = wait_packet(bob_socket, expected_sequence_number)

def run_bob() -> None:
    server_port = get_server_port()
    bob_socket = socket(AF_INET, SOCK_DGRAM)
    bob_socket.bind(('', server_port))
    serve(bob_socket)
    bob_socket.close()

run_bob()

