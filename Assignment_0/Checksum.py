import sys
from zlib import crc32

with open(sys.argv[1], "rb") as f:
    file_bytes = f.read()

checksum = crc32(file_bytes)
print(checksum)
