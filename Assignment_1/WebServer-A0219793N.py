import argparse
import re
from socket import *
from typing import List, Dict

SERVER_TIMEOUT = 1.5
HEADER_TERMINATOR = '  '
STORE = {}
COUNTER = {}

def ascii_encode(string: str) -> bytes:
    return string.encode('ascii')

def read_num_bytes(connection_socket: socket, num_bytes: int) -> bytes:
    bytes_read = bytes()
    while num_bytes > 0:
        read_bytes = connection_socket.recv(num_bytes)
        if len(read_bytes) > 0:
            bytes_read += read_bytes
            num_bytes -= len(read_bytes)
    return bytes_read
    
def GET(connection_socket: socket, path: str, header_key_values: Dict[str, str]) -> bytes:
    tokenized_path = [x for x in re.split('/', path) if x != '']
    prefix, key = tokenized_path[0], tokenized_path[1]

    def process_key(k: str) -> bytes:
        if k not in STORE:
            return ascii_encode('404 NotFound' + HEADER_TERMINATOR)
        content = STORE[k]
        if k in COUNTER:
            COUNTER[k] -= 1
            if COUNTER[k] < 1:
                COUNTER.pop(k)
                STORE.pop(k)        
        return ascii_encode('200 OK Content-Length ' + str(len(content)) + HEADER_TERMINATOR) + content

    def process_counter(k: str) -> bytes:
        if k in COUNTER:
            remaining_retrievals = COUNTER[k]
            return ascii_encode('200 OK Content-Length ' 
                + str(len(str(remaining_retrievals))) 
                + HEADER_TERMINATOR 
                + str(remaining_retrievals))
        if k in STORE:
            return ascii_encode('200 OK Content-Length 8' + HEADER_TERMINATOR + 'Infinity')
        return ascii_encode('404 NotFound' + HEADER_TERMINATOR)

    process_dispatch = {
        'key': process_key,
        'counter': process_counter,
    }

    return process_dispatch[prefix](key)

def POST(connection_socket: socket, path: str, header_key_values: Dict[bytes, bytes]) -> bytes:
    tokenized_path = [x for x in re.split('/', path) if x != '']
    prefix, key = tokenized_path[0], tokenized_path[1]
    content_length = int(header_key_values[b'CONTENT-LENGTH'].decode('ASCII'))  
    content = read_num_bytes(connection_socket, content_length)
    
    def process_key(k: str) -> bytes:
        if k in COUNTER:
            if COUNTER[k] > 0:
                return ascii_encode('405 MethodNotAllowed' + HEADER_TERMINATOR)
        STORE[k] = content
        return ascii_encode('200 OK' + HEADER_TERMINATOR)

    def process_counter(k: str) -> bytes:
        if k not in STORE:
            return ascii_encode('405 MethodNotAllowed' + HEADER_TERMINATOR)
        if k not in COUNTER:
            COUNTER[k] = 0
        COUNTER[k] += int(content.decode('ASCII'))
        return ascii_encode('200 OK' + HEADER_TERMINATOR)

    process_dispatch = {
        'key': process_key,
        'counter': process_counter,
    }

    return process_dispatch[prefix](key)

def DELETE(connection_socket: socket, path: str, header_key_values: Dict[str, str]) -> bytes:
    tokenized_path = [x for x in re.split('/', path) if x != '']
    prefix, key = tokenized_path[0], tokenized_path[1]
    if key not in STORE:
        return ascii_encode('404 NotFound' + HEADER_TERMINATOR)
    
    def process_key(k: str) -> bytes:
        content = STORE[k]
        if k in COUNTER:
            return ascii_encode('405 MethodNotAllowed' + HEADER_TERMINATOR)
        STORE.pop(k)
        return ascii_encode('200 OK Content-Length ' + str(len(content)) + HEADER_TERMINATOR) + content

    def process_counter(k: str) -> bytes:
        if k not in COUNTER:
            return ascii_encode('200 OK Content-Length 8' + HEADER_TERMINATOR + 'Infinity')
        remaining_retrievals = COUNTER[k]
        COUNTER.pop(k)
        return ascii_encode('200 OK Content-Length ' 
            + str(len(str(remaining_retrievals))) 
            + HEADER_TERMINATOR 
            + str(remaining_retrievals))

    process_dispatch = {
        'key': process_key,
        'counter': process_counter,
    }

    return process_dispatch[prefix](key)

HTTP_METHOD_DISPATCH = {
    'GET': GET,
    'POST': POST,
    'DELETE': DELETE
}

def get_server_port() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('server_port_number', type=int)
    args = parser.parse_args()
    return args.server_port_number

def create_server_socket(server_port: int) -> socket:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    return server_socket

def parse_header(connection_socket: socket) -> bytes:
    remaining_whitespace = 2
    header = bytes()
    while remaining_whitespace > 0:
        try:
            read_byte = connection_socket.recv(1)
            if read_byte == b' ':
                remaining_whitespace -= 1
            else:
                remaining_whitespace = 2
            header += read_byte
        except timeout:
            return header
    return header[:-2]

def parse_header_key_values(header_tokens: List[bytes]) -> Dict[bytes, bytes]:
    num_tokens = len(header_tokens)
    key_values = {}
    for i in range(0, num_tokens, 2):
        key = header_tokens[i].upper()
        value = header_tokens[i + 1]
        key_values[key] = value
    return key_values

def handle_socket(connection_socket: socket) -> None:
    connection_socket.settimeout(SERVER_TIMEOUT)

    while True:
        header_bytes = parse_header(connection_socket)
        if len(header_bytes) < 1:
            return
        header_tokens = header_bytes.split(b' ')
        method_name = header_tokens[0].decode('ASCII').upper()
        path = header_tokens[1].decode('ASCII')
        header_key_values = parse_header_key_values(header_tokens[2:])
        response = HTTP_METHOD_DISPATCH[method_name](connection_socket, path, header_key_values)
        connection_socket.send(response)

def serve(server_socket: socket):
    while True:
        server_socket.listen()
        connection_socket, client_address = server_socket.accept()
        print('HUI ZHUAN\'S SERVER')
        handle_socket(connection_socket)
        connection_socket.close()

def run_server():
    server_port = get_server_port()
    server_socket = create_server_socket(server_port)
    serve(server_socket)

run_server()
