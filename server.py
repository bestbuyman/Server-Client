import binascii
import socket
import struct
import sys
import argparse

def create_packet(**kwargs):
    print(kwargs)
    message_ver = socket.htons(kwargs['message_version'])
    message_typ = socket.htons(kwargs['message_type'])
    message_str = kwargs['message_string']
    data = struct.pack('!I', message_ver)  # pack the version
    data += struct.pack('!I', message_typ)  # pack the version
    data += struct.pack("!I", len(message_str))  # pack the length of string
    data += message_str.encode()  # pack the data
    return data


def run_command(command):
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument('-p', type=int, required=True, help='Port')
    parser.add_argument('-l', type=str, required=True, help='logFile')
    args = parser.parse_args()
    server_port = args.p
    log_file = args.l
    print(args)
    version = 17
    hello_message = "Hello"
    hello_packet = create_packet(message_version=version, message_type=1, message_string=hello_message)

    # create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 30001))
    sock.listen(5)
    while True:
        connection, address = sock.accept()
        print("Received connection from (IP, PORT): ", address)

        try:
            while True:

                data = connection.recv(struct.calcsize('!III'))
                print('received "%s"' % binascii.hexlify(data), len(data))
                if len(data) == 0:
                    break

                version_raw, message_type_raw, length_raw = struct.unpack('!III', data)
                version = socket.ntohs(version_raw)
                message_type = socket.ntohs(message_type_raw)
                length = socket.ntohs(length_raw)
                print('version: {0:d} message_type: {1:d} length: {2:d}'.format(version, message_type, length))
                if version == 17:
                    print("VERSION ACCEPTED")
                    message = connection.recv(length).decode()
                else:
                    print("VERSION MISMATCH")

                if message_type == 1:  # hello packet
                    connection.sendall(hello_packet)
                elif message_type == 2:  # command packet: LIGHTON
                    print("EXECUTING SUPPORTED COMMAND: ", message)
                    ret = run_command(message)
                    if ret == 0:  # success
                        connection.sendall(
                            create_packet(message_version=version, message_type=2, message_string="SUCCESS"))

                else:
                    print("IGNORING UNKNOWN COMMAND: ", message)

        finally:
            connection.close()
