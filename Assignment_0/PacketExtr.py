import sys

reader = sys.stdin.buffer
writer = sys.stdout.buffer
header_size = 6

while True:
    header_text = reader.read1(header_size)

    if len(header_text) < header_size:
        break

    num_bytes = ''

    while True:
        digit = reader.read1(1)
        if digit == b'B':
            break
        num_bytes += digit.decode('ASCII')

    num_bytes = int(num_bytes)
    data = reader.read1(num_bytes)
    writer.write(data)
    writer.flush()
