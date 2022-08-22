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

    num_bytes_to_read = int(num_bytes)

    while num_bytes_to_read > 0:
        data = reader.read1(num_bytes_to_read)
        writer.write(data)
        writer.flush()
        remaining_bytes_to_read = num_bytes_to_read - len(data)
        if remaining_bytes_to_read < 1:
            break
        num_bytes_to_read = remaining_bytes_to_read
