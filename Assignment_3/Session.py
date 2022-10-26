import os.path
from socket import *
import sys
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5, AES

RSA_KEY_LEN = 2048 // 8
BLOCK_SIZE = 16

def load_rsa_key(f_name_key="test/rsa_key.bin"):
    """
    load the public RSA key
    :return: RSA key
    """
    with open(f_name_key) as a:
        key = a.read()
    return RSA.import_key(key)

# connect to the server
if len(sys.argv) < 5:
    print ("Usage: python3 ", os.path.basename(__file__), "key_file_name data_file_name hostname/IP port")
else:
    key_file_name = sys.argv[1]
    data_file_name = sys.argv[2]
    serverName = sys.argv[3]
    serverPort = int(sys.argv[4])
    print (serverName, serverPort)

    rsa_key = load_rsa_key()

    # connect to the server
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((serverName, serverPort))

    # get the session key
    # first 256 bytes sent by the server is the RSA encrypted session key
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    ciphertext = client_socket.recv(RSA_KEY_LEN)
    session_key = cipher_rsa.decrypt(ciphertext, None)

    # write the session key to the file "key_file_name"
    key_file = open(key_file_name, 'w')
    key_file.write(session_key.decode())
    key_file.close()

    # get the data and write to file "data_file_name"
    cipher_aes = AES.new(session_key, AES.MODE_ECB)
    data_file = open(data_file_name, 'wb')

    # get the data from server
    while True:
        # decrypt the data in blocks of size 16B
        # size of data from the server is guaranteed to be a multiple of 16B
        data = client_socket.recv(BLOCK_SIZE)
        if len(data) < 1:
            break
        plaintext = cipher_aes.decrypt(data)
        data_file.write(plaintext)
    
    data_file.close()
    client_socket.close()
