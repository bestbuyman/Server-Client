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


# Create a TCP/IP socket

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLIENT")
    parser.add_argument('-s', type=str, required=True, help='Server IP')
    parser.add_argument('-p', type=int, required=True, help='Port')
    parser.add_argument('-l', type=str, required=True, help='logFile')
    args = parser.parse_args()
    server_ip = args.s
    server_port = args.p
    log_file = args.l
    version = 17
    hello_message = "Hello"
    hello_packet = create_packet(message_version=version, message_type=1, message_string=hello_message)

    command_message = "LIGHTON"
    command_packet_on = create_packet(message_version=version, message_type=2, message_string=command_message)

    command_message = "LIGHTOFF"
    command_packet_off = create_packet(message_version=version, message_type=2, message_string=command_message)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 30001)
    sock.connect(server_address)

    sock.sendall(hello_packet)

    try:
        while True:

            data = sock.recv(struct.calcsize('!III'))
            version_raw, message_type_raw, length_raw = struct.unpack('!III', data)
            version = socket.ntohs(version_raw)
            message_type = socket.ntohs(message_type_raw)
            length = socket.ntohs(length_raw)
            print('version: {0:d} type: {1:d} length: {2:d}'.format(version, message_type, length))
            if version == 17:
                print("VERSION ACCEPTED")
            else:
                print("VERSION MISMATCH")
            message = sock.recv(length).decode()
            print("Message", message)

            if message_type == 1:
                print("Sending command")
                sock.sendall(command_packet_on)  # or send off
            elif message_type == 2 and message == "SUCCESS":
                print("Command Successful")
                print('Closing socket')
                break
        fileLog = open(log_file, "w+")
        fileLog.write(message)
        fileLog.write(data)
        fileLog.close()

    finally:
        sock.close()
