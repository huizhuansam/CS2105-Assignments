# !/usr/bin/env python3
import os
import sys
from Cryptodome.Hash import SHA256

if len(sys.argv) < 3:
    print("Usage: python3 ", os.path.basename(__file__), "key_file_name document_file_name")
    sys.exit()

key_file_name = sys.argv[1]
file_name = sys.argv[2]

# get the authentication key from the file
KEY_NUM_BYTES = 32
with open(key_file_name, 'rb') as a:
    auth_key = a.read1(KEY_NUM_BYTES)

# read the input file
with open(file_name, 'rb') as a:
    input_file = a.read()

# First 32 bytes is the message authentication code
mac_from_file = input_file[:KEY_NUM_BYTES]

# Use the remaining file content to generate the message authentication code
h = SHA256.new()
data = input_file[KEY_NUM_BYTES:]
h.update(data + auth_key)
mac_generated = h.digest()

print('yes') if mac_from_file == mac_generated else print('no')
