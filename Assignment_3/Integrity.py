# !/usr/bin/env python3
import os
import sys
from Cryptodome.Hash import SHA256

if len(sys.argv) < 3:
    print("Usage: python3 ", os.path.basename(__file__), "key_file_name document_file_name")
    sys.exit()

key_file_name   = sys.argv[1]
file_name       = sys.argv[2]

# get the authentication key from the file
# TODO

# read the input file

# First 32 bytes is the message authentication code
# TODO
mac_from_file = "get me from the file"

# Use the remaining file content to generate the message authentication code
# TODO
mac_generated = "generated from the file"

if mac_from_file == mac_generated:
    print ('yes')
else:
    print ('no')
